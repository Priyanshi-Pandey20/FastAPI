from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    field_validator,
    model_validator,
    computed_field,
    EmailStr
)

from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime

#CREATE PYDANTIC

class DimensionCM(BaseModel):
    length:Annotated[float,Field(gt=0,strict=True,description="Length in cm")]
    width:Annotated[float,Field(gt=0,strict=True,description="Width in cm")]
    height:Annotated[float,Field(gt=0,strict=True,description="Height in cm")]



class Seller(BaseModel):

    id: UUID
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Seller Name",
            description="Name of the seller(2-60chars)",
            examples=["MI Store", "Apple Store India"]
        )
    ]
    email:EmailStr
    website:AnyUrl

        # SKU VALIDATOR
    @field_validator("email",mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):

       allowed_domains ={
           "mistore.in",
           "hpworld.in",
           "samsungindia.in",
           "lenovostore.in",
           "realmeoffice.in",
           "applestore.in",
           "dellexclusive.in",
           "oneplusstore.in",
           "asusexclusive.in",

            }
       domain = str(value).split("@")[-1].lower()
       if domain not in allowed_domains:
           raise ValueError(f"Seller email domain not allowed:{domain}")

       return value



class Product(BaseModel):

    id: UUID

    sku: Annotated[
        str,
        Field(
            min_length=6,
            max_length=30,
            title="SKU",
            description="Stock Keeping Unit",
            examples=["734-987-432"]
        )
    ]

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Product Name",
            description="Readable Product Name",
            examples=["Xiaomi Model Pro", "Apple Model X"]
        )
    ]

    description: Annotated[
        str,
        Field(
            max_length=300,
            description="Short product description"
        )
    ]

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            description="Category like Mobile/Electronics",
            examples=["Mobile", "Laptops"]
        )
    ]

    brand: Annotated[
        str,
        Field(
            min_length=2,
            max_length=80,
            examples=["Xiaomi", "Apple"]
        )
    ]

    price: Annotated[
        float,
        Field(
            gt=0,
            strict=True,
            description="Base price (INR)"
        )
    ]

    currency: Literal["INR"] = "INR"

    discount_percent: Annotated[
        int,
        Field(
            ge=0,
            le=100,
            strict=True,
            description="Discount percentage"
        )
    ]

    stock: Annotated[
        int,
        Field(
            ge=0,
            description="Available stock"
        )
    ]

    is_active: Annotated[
        bool,
        Field(description="Is product active?")
    ]

    rating: Annotated[
        float,
        Field(
            ge=0,
            le=5,
            strict=True,
            description="Rating out of 5"
        )
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(
            default=None,
            max_length=10,
            description="Up to 10 tags"
        )
    ]

    image_urls: Annotated[
        List[AnyUrl],
        Field(
            min_length=1,
            description="At least 1 image URL"
        )
    ]

    dimensions_cm :DimensionCM
    seller:Seller
    created_at: datetime


    # SKU VALIDATOR
    @field_validator("sku")
    @classmethod
    def validate_sku_format(cls, value: str):

        if "-" not in value:
            raise ValueError("SKU must contain '-'")

        last = value.split("-")[-1]

        if not (len(last) == 3 and last.isdigit()):
            raise ValueError(
                "SKU must end with 3 digits like 123"
            )

        return value

    # MODEL VALIDATOR
    @model_validator(mode="after")
    def validate_business_rules(self):

        if self.stock == 0 and self.is_active:
            raise ValueError(
                "If stock is 0, is_active must be False"
            )

        if self.discount_percent > 0 and self.rating == 0:
            raise ValueError(
                "Discounted product must have rating > 0"
            )

        return self
    
    #COMPUTED FIELD
    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1 -self.discount_percent/100),2)
    
    @computed_field
    @property
    def volume_cm3(self) -> float:
        d = self.dimensions_cm
        return round(d.length * d.width * d.height,2)
        
#UPDATE PYDANGTIC        
    
class DimensionsCMUpdate(BaseModel):
    length:Optional[float] = Field(gt=0)
    width:Optional[float] = Field(gt=0)
    height:Optional[float] = Field(gt=0)


class SellerUpdate(BaseModel):
    name:Optional[str] = Field(min_length=2,max_length=60)
    email:Optional[EmailStr]
    website:Optional[AnyUrl]

     # SKU VALIDATOR
    @field_validator("email",mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):

       allowed_domains ={
           "mistore.in",
           "hpworld.in",
           "samsungindia.in",
           "lenovostore.in",
           "realmeoffice.in",
           "applestore.in",
           "dellexclusive.in",
           "oneplusstore.in",
           "asusexclusive.in",

            }
       domain = str(value).split("@")[-1].lower()
       if domain not in allowed_domains:
           raise ValueError(f"Seller email domain not allowed:{domain}")

       return value


class ProductUpdate(BaseModel):

    name: Optional[str] = Field(default=None, min_length=3, max_length=80)
    description: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = None
    brand: Optional[str] = None

    price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[Literal["INR"]] = None

    discount_percent: Optional[int] = Field(default=None, ge=0, le=90)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)

    tags: Optional[List[str]] = Field(default=None, max_length=10)
    image_urls: Optional[List[AnyUrl]] = None

    dimensions_cm: Optional[DimensionsCMUpdate] = None
    seller: Optional[SellerUpdate] = None

    @model_validator(mode="after")
    def validate_business_rules(self):

        if self.stock == 0 and self.is_active:
            raise ValueError(
                "If stock is 0, is_active must be False"
            )

        if (
            self.discount_percent is not None
            and self.discount_percent > 0
            and self.rating == 0
        ):
            raise ValueError(
                "Discounted product must have rating > 0"
            )

        return self

    @computed_field
    @property
    def final_price(self) -> Optional[float]:

        if self.price is None or self.discount_percent is None:
            return None

        return round(
            self.price * (1 - self.discount_percent / 100),
            2
        )

    @computed_field
    @property
    def volume_cm3(self) -> Optional[float]:

        if self.dimensions_cm is None:
            return None

        d = self.dimensions_cm

        if d.length is None or d.width is None or d.height is None:
            return None

        return round(
            d.length * d.width * d.height,
            2
        )