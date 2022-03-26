import resources.Environment as Env
from src.model.enums.Region import Region


class Location:
    """
    Class for Locations
    """

    def __init__(self, level: int, name: str, region: Region, required_bounty: int, show_poster: bool, image_url: str):
        """
        Initialize the Location object
        :param level: The level of the location
        :param name: The name of the location
        :param region: The region of the location
        :param required_bounty: The required bounty to enter the location
        :param show_poster: If to show a generated bounty poster image for the location
        :param image_url: The url of the image
        """
        self.level = level
        self.name = name
        self.region = region
        self.required_bounty = required_bounty
        self.show_poster = show_poster
        self.image_url = image_url

    def is_paradise(self) -> bool:
        """
        Check if the location is a paradise
        :return: True if the location is a paradise
        """
        return is_paradise_by_level(self.level)

    def is_new_world(self) -> bool:
        """
        Check if the location is a new world
        :return: True if the location is a new world
        """
        return not is_paradise_by_level(self.level)


ND = Location(0, "None", Region.ND, 0, False, '')
FOOSHA_VILLAGE = Location(1, 'Foosha Village', Region.PARADISE, 0, False, Env.LOCATION_FOOSHA_VILLAGE_IMAGE_URL.get())
SHELLS_TOWN = Location(2, 'Shells Town', Region.PARADISE, 1000000, False, Env.LOCATION_SHELLS_TOWN_IMAGE_URL.get())
ORANGE_TOWN = Location(3, 'Orange Town', Region.PARADISE, 3000000, False, Env.LOCATION_ORANGE_TOWN_IMAGE_URL.get())
ISLAND_OF_RARE_ANIMALS = Location(4, 'Island of Rare Animals', Region.PARADISE, 6000000, False,
                                  Env.LOCATION_ISLAND_OF_RARE_ANIMALS_IMAGE_URL.get())
SYRUP_VILLAGE = Location(5, 'Syrup Village', Region.PARADISE, 10000000, False,
                         Env.LOCATION_SYRUP_VILLAGE_IMAGE_URL.get())
BARATIE = Location(6, 'Baratie', Region.PARADISE, 15000000, False, Env.LOCATION_BARATIE_IMAGE_URL.get())
ARLONG_PARK = Location(7, 'Arlong Park', Region.PARADISE, 21000000, False, Env.LOCATION_ARLONG_PARK_IMAGE_URL.get())
LOUGETOWN = Location(8, 'Lougetown', Region.PARADISE, 30000000, True, Env.LOCATION_LOUGETOWN_IMAGE_URL.get())
REVERSE_MOUNTAIN = Location(9, 'Reverse Mountain', Region.PARADISE, 35000000, False,
                            Env.LOCATION_REVERSE_MOUNTAIN_IMAGE_URL.get())
WHISKEY_PEAK = Location(10, 'Whiskey Peak', Region.PARADISE, 42000000, False, Env.LOCATION_WHISKEY_PEAK_IMAGE_URL.get())
LITTLE_GARDEN = Location(11, 'Little Garden', Region.PARADISE, 55000000, False,
                         Env.LOCATION_LITTLE_GARDEN_IMAGE_URL.get())
DRUM_ISLAND = Location(12, 'Drum Island', Region.PARADISE, 70000000, False, Env.LOCATION_DRUM_ISLAND_IMAGE_URL.get())
ARABASTA_KINGDOM = Location(13, 'Arabasta Kingdom', Region.PARADISE, 80000000, False,
                            Env.LOCATION_ARABASTA_KINGDOM_IMAGE_URL.get())
JAYA = Location(14, 'Jaya', Region.PARADISE, 100000000, False, Env.LOCATION_JAYA_IMAGE_URL.get())
SKYPIEA = Location(15, 'Skypiea', Region.PARADISE, 120000000, True, Env.LOCATION_SKYPIEA_IMAGE_URL.get())
LONG_RING_LONG_LAND = Location(16, 'Long Ring Long Land', Region.PARADISE, 150000000, False,
                               Env.LOCATION_LONG_RING_LONG_LAND_IMAGE_URL.get())
WATER_7 = Location(17, 'Water 7', Region.PARADISE, 190000000, False, Env.LOCATION_WATER_7_IMAGE_URL.get())
ENIES_LOBBY = Location(18, 'Enies Lobby', Region.PARADISE, 240000000, False, Env.LOCATION_ENIES_LOBBY_IMAGE_URL.get())
THRILLER_BARK = Location(19, 'Thriller Bark', Region.PARADISE, 300000000, True,
                         Env.LOCATION_THRILLER_BARK_IMAGE_URL.get())
SABAODY_ARCHIPELAGO = Location(20, 'Sabaody Archipelago', Region.PARADISE, 350000000, False,
                               Env.LOCATION_SABAODY_ARCHIPELAGO_IMAGE_URL.get())
FISHMAN_ISLAND = Location(21, 'Fish-Man Island', Region.NEW_WORLD, 400000000, True,
                          Env.LOCATION_FISHMAN_ISLAND_IMAGE_URL)
PUNK_HAZARD = Location(22, 'Punk Hazard', Region.NEW_WORLD, 420000000, False, Env.LOCATION_PUNK_HAZARD_IMAGE_URL.get())
DRESSROSA = Location(23, 'Dressrosa', Region.NEW_WORLD, 450000000, False, Env.LOCATION_DRESSROSA_IMAGE_URL)
ZOU = Location(24, 'Zou', Region.NEW_WORLD, 500000000, True, Env.LOCATION_ZOU_IMAGE_URL.get())
WHOLE_CAKE_ISLAND = Location(25, 'Whole Cake Island', Region.NEW_WORLD, 800000000, False,
                             Env.LOCATION_WHOLE_CAKE_ISLAND_IMAGE_URL.get())
WANO_COUNTRY = Location(26, 'Wano Country', Region.NEW_WORLD, 1500000000, True,
                        Env.LOCATION_WANO_COUNTRY_IMAGE_URL.get())

LOCATIONS = [ND, FOOSHA_VILLAGE, SHELLS_TOWN, ORANGE_TOWN, ISLAND_OF_RARE_ANIMALS, SYRUP_VILLAGE, BARATIE, ARLONG_PARK,
             LOUGETOWN, REVERSE_MOUNTAIN, WHISKEY_PEAK, LITTLE_GARDEN, DRUM_ISLAND, ARABASTA_KINGDOM, JAYA, SKYPIEA,
             LONG_RING_LONG_LAND, WATER_7, ENIES_LOBBY, THRILLER_BARK, SABAODY_ARCHIPELAGO, FISHMAN_ISLAND, PUNK_HAZARD,
             DRESSROSA, ZOU, WHOLE_CAKE_ISLAND, WANO_COUNTRY]


def get_by_bounty(bounty: int) -> Location:
    """
    Get a Location by a bounty
    """
    for location in reversed(LOCATIONS):
        # If the bounty is greater than or equal to the required bounty, return the location
        if bounty >= location.required_bounty:
            return location

    raise ValueError('No location found for bounty: {}'.format(bounty))


def get_by_level(level: int) -> Location:
    """
    Get a Location by a level
    """
    for location in LOCATIONS:
        if location.level == level:
            return location

    raise ValueError('No location found for level: {}'.format(level))


def is_paradise_by_level(level: int) -> bool:
    """
    Check if a location is a paradise by a level
    :param level: The level of the location
    :return: True if the location is a paradise, False otherwise
    """
    return get_by_level(level).region == Region.PARADISE


def is_new_world_by_level(level: int) -> bool:
    """
    Check if a location is a new world by a level
    :param level: The level of the location
    :return: True if the location is a new world, False otherwise
    """
    return get_by_level(level).region == Region.NEW_WORLD


def get_first_new_world() -> Location:
    """
    Get the first new world location
    """
    for location in LOCATIONS:
        if location.region == Region.NEW_WORLD:
            return location

    raise ValueError('No new world location found')


def get_last_paradise() -> Location:
    """
    Get the last paradise location
    """
    for location in reversed(LOCATIONS):
        if location.region == Region.PARADISE:
            return location

    raise ValueError('No paradise location found')
