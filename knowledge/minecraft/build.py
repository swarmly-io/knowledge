import json
from time import perf_counter
from knowledge.elastic_client import ElasticClient
from knowledge.minecraft.mcd_utils import get_item_model_by_name
from knowledge.minecraft.models.entity_models import BlockDrops, Drop, EntitiesDmg, EntityDrops, EntityMc
from knowledge.minecraft.models.normalised_models import Recipe, BaseItem, RecipeItem, Block, RecipeList, Food, SmeltingRecipe
from knowledge.util import rec_flatten


def normalise_and_load_recipes(es, mcd):
    recipe_ids = [r for r in mcd.recipes]
    recipes = [(id, mcd.recipes[id]) for id in recipe_ids]
    norm_recipes = []
    for rid, r in recipes:
        recipe_list = RecipeList(id=rid)
        for ir in r:
            item_list = []
            items = {}
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
                item = RecipeItem(
                    id=it['id'],
                    display_name=it['displayName'],
                    name=it['name'],
                    stack_size=it['stackSize'],
                    quantity=it['quantity'])
                item_list.append(item)

            oit = mcd.find_item_or_block(ir['result']['id'])
            count = ir['result']['count']
            output_item = RecipeItem(
                id=oit['id'],
                display_name=oit['displayName'],
                name=oit['name'],
                stack_size=oit['stackSize'],
                quantity=count)
            recipe_item = Recipe(needs=item_list, provides=output_item)
            recipe_list.items.append(recipe_item)
        norm_recipes.append(recipe_list)

        es.bulk_load(norm_recipes)


def normalise_and_load_blocks(es, mcd):
    block_ids = [r for r in mcd.blocks]
    blocks = [(id, mcd.blocks[id]) for id in block_ids]
    norm_blocks = []
    for bid, block in blocks:
        items = []
        drops = []
        for id, _ in (block.get('harvestTools') or {}).items():
            req = mcd.find_item_or_block(int(id))
            items.append(
                BaseItem(
                    id=int(
                        req['id']),
                    display_name=req['displayName'],
                    name=req['name'],
                    stack_size=req['stackSize'],
                    max_durability=req['maxDurability']))

        for id in block.get('drops') or []:
            drop = mcd.find_item_or_block(id)
            drops.append(
                BaseItem(
                    id=drop['id'],
                    display_name=drop['displayName'],
                    name=drop['name'],
                    stack_size=drop['stackSize']))

        block = Block(
            id=bid,
            name=block['name'],
            material=block['material'],
            diggable=block['diggable'],
            display_name=block["displayName"],
            hardness=block.get('hardness'),
            resistance=block.get('resistance'),
            requires=items,
            drops=drops)
        norm_blocks.append(block)
    es.bulk_load(norm_blocks)


def normalise_and_load_items(es, mcd):
    items = []
    for item_name in mcd.items_name.keys():
        items.append(get_item_model_by_name(mcd, item_name))
    es.bulk_load(items)


def normalise_and_load_foods(es, mcd):
    foods = []
    for food in mcd.foods.values():
        foods.append(Food(
            id=food['id'],
            display_name=food['displayName'],
            name=food['name'],
            stack_size=food['stackSize'],
            food_points=food['foodPoints'],
            saturation=food['saturation'],
            effective_quality=food['effectiveQuality'],
            saturation_ratio=food['saturationRatio']
        ))
    es.bulk_load(foods)


def load_smelting_recipes(es):
    with open("./knowledge/extraction/data/smelting_recipes.json") as file:
        smelting = json.load(file)
    entries = []
    for s in smelting:
        e = SmeltingRecipe(**s)
        entries.append(e)
    es.bulk_load(entries)


def load_entities(es):
    with open("./knowledge/extraction/data/entities.json") as file:
        entities = json.load(file)
    entries = []
    for en in entities:
        e = EntityMc(**en)
        entries.append(e)
    es.bulk_load(entries)


def load_hostile_entities_dmg(es):
    with open("./knowledge/extraction/data/entities_dmg.json") as file:
        entities = json.load(file)
    entries = []
    for en in entities:
        e = EntitiesDmg(**en)
        entries.append(e)
    es.bulk_load(entries)


def load_entity_loot(es, mcd):
    loot = mcd.entityLoot
    entries = []
    for l in loot:
        drops = loot[l]
        el = EntityDrops(id=l, entity=l, drops=[Drop(**d) for d in drops])
        entries.append(el)
    es.bulk_load(entries)


def load_block_loot(es, mcd):
    loot = mcd.blockLoot
    entries = []
    for l in loot:
        drops = loot[l]
        el = BlockDrops(id=l, block=l, drops=[Drop(**d) for d in drops])
        entries.append(el)
    es.bulk_load(entries)


def create_minecraft_indexes(elastic_config):
    import minecraft_data
    # Java edition minecraft-data
    mcd = minecraft_data("1.17.1")

    esen = elastic_config.get_elastic_client("entities")
    load_entities(esen)
    print("Completed loading entities")

    esdmg = elastic_config.get_elastic_client("entitiesdmg")
    load_hostile_entities_dmg(esdmg)
    print("Completed loading hostile entities dmg")

    esbl = elastic_config.get_elastic_client("blockloot")
    load_block_loot(esbl, mcd)
    print("Completed blockloot")

    esl = elastic_config.get_elastic_client("entityloot")
    load_entity_loot(esl, mcd)
    print("Completed entityloot")

    ess = elastic_config.get_elastic_client("smelting")
    load_smelting_recipes(ess)
    print("Completed smelting")

    es = elastic_config.get_elastic_client("recipe")
    normalise_and_load_recipes(es, mcd)
    print("Completed recipe")

    esb = elastic_config.get_elastic_client("blocks")
    normalise_and_load_blocks(esb, mcd)
    print("Completed blocks")

    esi = elastic_config.get_elastic_client("items")
    normalise_and_load_items(esi, mcd)
    print("Completed items")

    es_foods = elastic_config.get_elastic_client("foods")
    normalise_and_load_foods(es_foods, mcd)
    print("Completed foods")


if __name__ == '__main__':
    import minecraft_data

    # Java edition minecraft-data
    mcd = minecraft_data("1.17.1")
    es = ElasticClient.get_elastic_client("recipe")

    t1_start = perf_counter()

    print(es.search_all(692))
    print(es.search_all(30))

    print(es.search_all(50))

    # mcd.find_item_or_block(692)

    t1_stop = perf_counter()
    print('elapsed', t1_stop - t1_start)

    # print(es.search("iron_pickaxe"))
    # data = es.get(7)
    # x = Recipe(**data)
    # print(x)
    # print(es.search("andesite"))
