import typer

from prisma import Client
from taskforce.cli.async_typer import AsyncTyper

org_app = AsyncTyper()
prisma_client = Client()


@org_app.async_command()
async def list():
    async with prisma_client:
        organizations = await prisma_client.organization.find_many()
        if len(organizations) > 0:
            for org in organizations:
                typer.echo(f"{org.id}: {org.name}")
        else:
            typer.echo("No organizations found")


@org_app.async_command()
async def show(org_id: str):
    async with prisma_client:
        org = await prisma_client.organization.find_unique(where={"id": org_id})
        if org:
            typer.echo(f"{org.id}: {org.name}")
        else:
            typer.echo("Organization not found")


@org_app.async_command()
async def create(org_name: str, description=None, logo: str = None, url: str = None):
    async with prisma_client:
        org = await prisma_client.organization.create(
            data={
                "name": org_name,
                "description": description,
                "logo": logo,
                "url": url,
                "owner_userId": {
                    "name": "John Doe",
                },
            }
        )
        typer.echo(f"Created organization: {org.id}: {org.name}")


@org_app.async_command()
async def delete(org_id: str):
    async with prisma_client:
        org = await prisma_client.organization.delete(where={"id": org_id})
        typer.echo(f"Deleted organization: {org.id}: {org.name}")


@org_app.async_command()
async def invite(org_id: str, user_id: str):
    async with prisma_client:
        org = await prisma_client.organization.update(
            where={"id": org_id},
            data={"users": {"connect": {"id": user_id}}},
        )
        typer.echo(f"Invited user {user_id} to organization {org.id}: {org.name}")


@org_app.async_command()
async def kick(org_id: str, user_id: str):
    async with prisma_client:
        org = await prisma_client.organization.update(
            where={"id": org_id},
            data={"users": {"disconnect": {"id": user_id}}},
        )
        typer.echo(f"Kicked user {user_id} from organization {org.id}: {org.name}")


@org_app.async_command()
async def users(org_id: str):
    async with prisma_client:
        org = await prisma_client.organization.find_unique(
            where={"id": org_id},
            include={"users": True},
        )
        if org:
            typer.echo(f"Users in organization {org.id}: {org.name}")
            for user in org.users:
                typer.echo(f"{user.id}: {user.name}")
        else:
            typer.echo("Organization not found")


@org_app.async_command()
async def owners(org_id: str):
    async with prisma_client:
        org = await prisma_client.organization.find_unique(
            where={"id": org_id},
            include={"owner_user": True},
        )
        if org:
            typer.echo(f"Owner of organization {org.id}: {org.name}")
            typer.echo(f"{org.owner_user.id}: {org.owner_user.name}")
        else:
            typer.echo("Organization not found")


@org_app.async_command()
async def add_owner(org_id: str, user_id: str):
    async with prisma_client:
        org = await prisma_client.organization.update(
            where={"id": org_id},
            data={"owner_user": {"connect": {"id": user_id}}},
        )
        typer.echo(f"Added owner {user_id} to organization {org.id}: {org.name}")


@org_app.async_command()
async def remove_owner(org_id: str, user_id: str):
    async with prisma_client:
        org = await prisma_client.organization.update(
            where={"id": org_id},
            data={"owner_user": {"disconnect": True}},
        )
        typer.echo(f"Removed owner {user_id} from organization {org.id}: {org.name}")
