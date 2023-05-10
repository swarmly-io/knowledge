from time import perf_counter
from knowledge.elastic_client import ElasticClient
from knowledge.minecraft.models.normalised_models import Recipe, Item, RecipeItem, Block, FurnaceRecipe
from knowledge.util import rec_flatten
from mcd_utils import get_item_model_by_name

def normalise_and_load_recipes(es, mcd):
    recipe_ids = [r for r in mcd.recipes]
    recipes = [(id,mcd.recipes[id]) for id in recipe_ids]
    norm_recipes = []
    for rid, r in recipes:
        recipe = Recipe(id = rid)
        for ir in r:
            item_list = []
            items={}
            if ir.get('inShape'):
                ing = rec_flatten(ir.get('inShape'))
            else:
                ing = ir.get('ingredients')
            
            for ins in ing:
                if not ins:
                    continue
                
                if items.get(ins):
                    quantity = items[ins]['quantity'] + 1
                else:
                    quantity = 1
                items[ins] = mcd.find_item_or_block(ins)
                items[ins]['quantity'] = quantity
                
            for i in items:
                it = items[i]
                item = Item(id=it['id'], display_name=it['displayName'], name=it['name'], stack_size=it['stackSize'], quantity=it['quantity'])
                item_list.append(item)
                
            oit = mcd.find_item_or_block(ir['result']['id'])
            count = ir['result']['count']
            output_item = Item(id=oit['id'], display_name=oit['displayName'], name=oit['name'], stack_size=oit['stackSize'], quantity=count)
            recipe_item = RecipeItem(needs = item_list, provides=output_item)
            recipe.items.append(recipe_item)
        norm_recipes.append(recipe)
        
        es.bulk_load(norm_recipes)
        
def normalise_and_load_blocks(es, mcd):
    block_ids = [r for r in mcd.blocks]
    blocks = [(id,mcd.blocks[id]) for id in block_ids]
    norm_blocks = []
    for bid, block in blocks:
        items = []
        drops = []
        for id, _ in (block.get('harvestTools') or {}).items():
            req = mcd.find_item_or_block(int(id))
            items.append(Item(id=int(req['id']), display_name=req['displayName'], name=req['name'], stack_size=req['stackSize'], quantity=1, max_durability=req['maxDurability']))
        
        for id in block.get('drops') or []:
            drop = mcd.find_item_or_block(id)
            drops.append(Item(id=drop['id'], display_name=drop['displayName'], name=drop['name'], stack_size=drop['stackSize'], quantity=1))
            
        block = Block(id=bid, display_name=block["displayName"], name=block['name'], hardness=block.get('hardness'), resistance=block.get('resistance'), requires=items, drops=drops)
        norm_blocks.append(block)
    es.bulk_load(norm_blocks)

def normalise_and_load_furnace_recipes(es, be_mcd, j_mcd):
    recipe_ids = [r for r in be_mcd.recipes]
    recipes = [(id, be_mcd.recipes[id]) for id in recipe_ids]

    recipes = filter(
        lambda recipe: recipe[1]['type'] == "furnace",
        recipes)

    norm_recipes = []
    for rid, recipe in recipes:
        input = recipe['ingredients'][0] # always has one input and one output
        input_item = get_item_model_by_name(j_mcd, input['name'], bedrock=True)
        input_item.quantity = input['count']

        output = recipe['output'][0]
        output_item = get_item_model_by_name(j_mcd, output['name'], bedrock=True)
        output_item.quantity = output['count']

        model = FurnaceRecipe(id=rid, input=input_item, output=output_item)

        norm_recipes.append(model)
    es.bulk_load(norm_recipes)

def create_minecraft_indexes():
    import minecraft_data
    # Java edition minecraft-data
    mcd = minecraft_data("1.17.1")
    
    es = ElasticClient.get_elastic_client("recipe")
    normalise_and_load_recipes(es, mcd)
    esb = ElasticClient.get_elastic_client("blocks")
    normalise_and_load_blocks(esb, mcd)

    # furnace recipes are supported only in bedrock edition of minecraft
    esf = ElasticClient.get_elastic_client("furnace_recipes")
    mcd_be = minecraft_data("1.17.10", edition='bedrock')
    normalise_and_load_furnace_recipes(esf, mcd_be, mcd)

if __name__ == '__main__':
    import minecraft_data
    # Java edition minecraft-data
    mcd = minecraft_data("1.17.1")
    es = ElasticClient.get_elastic_client("recipe")

    t1_start = perf_counter()

    print(es.search_all(692))
    print(es.search_all(30))

    print(es.search_all(50))

    #mcd.find_item_or_block(692)
    
    t1_stop = perf_counter()
    print('elapsed', t1_stop-t1_start)



    #print(es.search("iron_pickaxe"))
    # data = es.get(7)
    # x = Recipe(**data)
    # print(x)
    # print(es.search("andesite"))
                    
        
        