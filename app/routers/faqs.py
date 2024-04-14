from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_db
from pymongo import MongoClient
from ..schemas.services import FAQ
from typing import List


router = APIRouter(prefix="/service-providers", tags=["FAQs"])


@router.get("/{sp_username}/services/{service_name}/faqs", response_model=List[FAQ])
def get_faqs_by_service(
    sp_username: str, service_name: str, db: MongoClient = Depends(get_db)
):
    service_provider = db["serviceProviders"].find_one({"username": sp_username})

    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found",
        )

    services = service_provider.get("services", [])
    matching_service = None
    for service in services:
        if service.get("name") == service_name:
            matching_service = service
            break

    if not matching_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found for serviceProvider '{sp_username}'",
        )

    faqs = matching_service.get("faqs", [])

    return faqs


@router.post("/{sp_username}/services/{service_name}/faqs")
def create_faq(
    sp_username: str, service_name: str, FAQ: FAQ, db: MongoClient = Depends(get_db)
):
    service_provider = db["serviceProviders"].find_one({"username": sp_username})
    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found",
        )

    services = service_provider.get("services", [])
    matching_service = None
    for service in services:
        if service.get("name") == service_name:
            matching_service = service
            break

    if not matching_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found for serviceProvider '{sp_username}'",
        )

    db["serviceProviders"].update_one(
        {"username": sp_username, "services.name": service_name},
        {"$push": {"services.$.faqs": FAQ.model_dump()}},
    )

    return {"message": "FAQ created successfully"}


@router.delete("/{sp_username}/services/{service_name}/faqs/{faq_question}")
def delete_faq_by_question(
    sp_username: str,
    service_name: str,
    faq_question: str,
    db: MongoClient = Depends(get_db),
):
    result = db["serviceProviders"].update_one(
        {"username": sp_username, "services.name": service_name},
        {
            "$pull": {
                "services.$.faqs": {
                    "question": faq_question,
                    "answer": {"$exists": True},
                }
            }
        },
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ with question '{faq_question}' not found for service '{service_name}'",
        )

    return {"message": f"FAQ with question '{faq_question}' deleted successfully"}


@router.delete("/{sp_username}/services/{service_name}/faqs")
def delete_all_faqs(
    sp_username: str, service_name: str, db: MongoClient = Depends(get_db)
):
    result = db["serviceProviders"].update_one(
        {"username": sp_username, "services.name": service_name},
        {"$unset": {"services.$.faqs": ""}},
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No FAQs found for service '{service_name}'",
        )

    return {"message": f"All FAQs for service '{service_name}' deleted successfully"}
