from knowledge.minecraft.models.normalised_models import RecipeItem

# very annoyingly, some bedrock items are named differently in
# java edition, for example the wood types.
bedrock_to_java_item_names = {
    "wood": "oak_wood",
    "log": "oak_log",
    "hardened_clay": "terracotta",
    "netherbrick": 'nether_brick',
    "stonebrick": 'stone_bricks',
    'quartz_ore': 'nether_quartz_ore',
    'stained_hardened_clay': 'white_terracotta',
    'silver_glazed_terracotta': 'light_gray_glazed_terracotta',
    'log2': 'acacia_log'
}


def bedrock_to_java_item_name(name):
    if name not in bedrock_to_java_item_names:
        return name

    return bedrock_to_java_item_names[name]


def get_recipe_item_model_by_name(mcd, name, quantity, bedrock=False):
    if bedrock:
        name = bedrock_to_java_item_name(name)

    entry = mcd.items_name[name]
    durability = entry['maxDurability'] if 'maxDurability' in entry else None

    return RecipeItem(id=entry['id'],
                      display_name=entry['displayName'],
                      name=entry['name'],
                      stack_size=entry['stackSize'],
                      max_durability=durability,
                      quantity=quantity)
