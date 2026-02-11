"""Endee MCP Framework - Backup tools."""

from typing import Any


async def endee_create_backup(
    index_name: str,
    backup_name: str,
) -> dict[str, Any]:
    """Create a backup of an index.
    
    Args:
        index_name: Name of the index to backup
        backup_name: Name for the backup
    
    Returns:
        Success message
    """
    from ..server import endee_client
    
    return await endee_client.create_backup(index_name, backup_name)


async def endee_list_backups() -> dict[str, Any]:
    """List all available backups.
    
    Returns:
        List of backup names
    """
    from ..server import endee_client
    
    backups = await endee_client.list_backups()
    return {"backups": backups}


async def endee_restore_backup(
    backup_name: str,
    target_index_name: str,
) -> dict[str, Any]:
    """Restore a backup to a new index.
    
    Args:
        backup_name: Name of the backup to restore
        target_index_name: Name for the restored index
    
    Returns:
        Success message
    """
    from ..server import endee_client
    
    return await endee_client.restore_backup(backup_name, target_index_name)


async def endee_delete_backup(
    backup_name: str,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a backup.
    
    Args:
        backup_name: Name of the backup to delete
        confirm: Must be True to confirm
    
    Returns:
        Success message
    
    Raises:
        ValueError: If confirm is not True
    """
    if not confirm:
        raise ValueError("Must set confirm=True to delete backup")
    
    from ..server import endee_client
    
    return await endee_client.delete_backup(backup_name)
