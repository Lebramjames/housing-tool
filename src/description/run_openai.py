# %%
# Description output: 
# Balkon richting e.g. zuidwest
# Renovatie nodig, subcategorieën: keuken, badkamer, volledig huis





# %%
# we iterate over the 

from pydantic import BaseModel, Field

class ContactViewing(BaseModel):
    agency: str = Field(None, description="Name of the agency")
    contact: str = Field(None, description="Contact person for the viewing")

class Renovation(BaseModel):
    kitchen: bool = Field(None, description="Whether the kitchen needs renovation")
    bathroom: bool = Field(None, description="Whether the bathroom needs renovation")
    full_house: bool = Field(None, description="Whether the full house needs renovation")

class Transportation(BaseModel):
    metro_minutes: int = Field(None, description="Minutes to nearest metro station")
    tram_minutes: int = Field(None, description="Minutes to nearest tram stop")
    highway_minutes: int = Field(None, description="Minutes to nearest highway")


class AllInformation(BaseModel):
    contact_viewing: ContactViewing = Field(None, description="Contact and agency information for viewing")
    property_information: PropertyInformation = Field(None, description="Detailed property information")
    renovation: Renovation = Field(None, description="Renovation needs for kitchen, bathroom, or full house")
    transportation: Transportation = Field(None, description="Transportation options and distances")

