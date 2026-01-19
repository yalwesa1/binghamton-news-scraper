from pydantic import BaseModel


class Venue(BaseModel):
    """
    Represents the data structure of a News Story from Binghamton University.
    All fields are required for complete story extraction.
    """

    story_title: str
    story_category: str
    story_summary: str
    story_LinkedIn_post: str
