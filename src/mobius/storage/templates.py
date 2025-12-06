"""
Template storage operations.

Provides CRUD operations for template entities in Supabase.
"""

from mobius.models.template import Template
from mobius.storage.database import get_supabase_client
from typing import List, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


class TemplateStorage:
    """Storage operations for template entities."""

    def __init__(self):
        self.client = get_supabase_client()

    async def create_template(self, template: Template) -> Template:
        """
        Create a new template in the database.

        Args:
            template: Template entity to create

        Returns:
            Template: Created template with database-generated fields

        Raises:
            Exception: If database operation fails
        """
        logger.info(
            "creating_template",
            template_id=template.template_id,
            brand_id=template.brand_id,
            name=template.name,
        )

        data = template.model_dump()
        result = self.client.table("templates").insert(data).execute()

        logger.info("template_created", template_id=template.template_id)
        return Template.model_validate(result.data[0])

    async def get_template(self, template_id: str) -> Optional[Template]:
        """
        Retrieve a template by ID.

        Args:
            template_id: UUID of the template

        Returns:
            Template if found, None otherwise
        """
        logger.debug("fetching_template", template_id=template_id)

        result = (
            self.client.table("templates")
            .select("*")
            .eq("template_id", template_id)
            .is_("deleted_at", "null")
            .execute()
        )

        if result.data:
            return Template.model_validate(result.data[0])
        return None

    async def list_templates(self, brand_id: str, limit: int = 100) -> List[Template]:
        """
        List all templates for a brand.

        Args:
            brand_id: UUID of the brand
            limit: Maximum number of templates to return

        Returns:
            List of Template entities
        """
        logger.debug("listing_templates", brand_id=brand_id, limit=limit)

        result = (
            self.client.table("templates")
            .select("*")
            .eq("brand_id", brand_id)
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return [Template.model_validate(t) for t in result.data]

    async def update_template(self, template_id: str, updates: dict) -> Template:
        """
        Update template fields.

        Args:
            template_id: UUID of the template
            updates: Dictionary of fields to update

        Returns:
            Updated Template entity

        Raises:
            Exception: If template not found or update fails
        """
        logger.info(
            "updating_template", template_id=template_id, fields=list(updates.keys())
        )

        # Add updated_at timestamp
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("templates")
            .update(updates)
            .eq("template_id", template_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Template {template_id} not found")

        logger.info("template_updated", template_id=template_id)
        return Template.model_validate(result.data[0])

    async def delete_template(self, template_id: str) -> bool:
        """
        Soft delete a template.

        Sets deleted_at timestamp instead of removing the record.

        Args:
            template_id: UUID of the template

        Returns:
            True if successful

        Raises:
            Exception: If template not found or delete fails
        """
        logger.info("soft_deleting_template", template_id=template_id)

        result = (
            self.client.table("templates")
            .update({"deleted_at": datetime.now(timezone.utc).isoformat()})
            .eq("template_id", template_id)
            .execute()
        )

        if not result.data:
            raise ValueError(f"Template {template_id} not found")

        logger.info("template_soft_deleted", template_id=template_id)
        return True
