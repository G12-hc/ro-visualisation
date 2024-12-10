import os
# import sys
from datetime import datetime

from app.count_lines import analyze_repository
from app.db import get_db_connection
from app.db.fetch_git_api import get_repository_details, get_commit_history, get_files, fetch_lang_details, \
    get_contributors
from app.db.queries import query_insert_commits, query_insert_repository, query_insert_files, query_insert_branches, \
    query_insert_licenses, query_insert_language


async def assign_repo_data(owner: str, repo: str):
    conn = get_db_connection()
    try:
        repo_details = await get_repository_details(owner, repo)
        commit_data = await get_commit_history(owner, repo)
        default_branch = repo_details.get("default_branch", "main")
        file_data = await get_files(owner, repo, default_branch)
        lang_data = await fetch_lang_details(owner, repo)
        contributor_data = await get_contributors(owner, repo)
        # repo data
        repository_id = f"github-{repo_details['id']}"
        workspace_id = None  # Assign workspace ID dynamically if available, not sure what to put
        licence_id = None # Is assigned after inset attempt
        user_ids = [user["id"] for user in contributor_data]
        print(user_ids)
        archieved_user_ids = [0]
        linked_status= "Linked"

        # Licence
        if repo_details["license"] is None:
            print("No licenses found")
        else:
             licence_id = query_insert_licenses(
                conn,
                repo_details["license"]["key"],
                repo_details["license"]["name"],
                repo_details["license"]["spdx_id"],
                repo_details["license"]["url"],
                repo_details["license"]["node_id"]
            )

        # Repository
        query_insert_repository(
            conn,
            repository_id,
            repo_details["id"],
            repo_details["watchers"],
            repo_details["forks_count"],
            repo_details["name"],
            repo_details["owner"]["login"],
            linked_status,  # not sure what to put for linked
            datetime.now(),
            datetime.now(),
            repo_details["contributors_url"],
            default_branch,
            user_ids,
            archieved_user_ids,  # Archived user IDs
            licence_id,
            workspace_id,
        )

        # Files
        for file in file_data.get("tree", []):
            path = file["path"]
            analyzed_files = await analyze_repository(owner, repo, default_branch)
            for file_info in analyzed_files:
                total_lines = file_info["total_lines"]
                functional_lines = file_info["functional_lines"]
                query_insert_files(
                    conn,
                    file["type"] == "tree",  # is directory true
                    path,
                    os.path.basename(path),
                    total_lines,  # total line count
                    functional_lines,  # functional lines
                    None,  # symlinkTarget placeholder as I am unsure
                    "branch_id_placeholder",  # Replace dynamically,
                    # improve query to match a branch ID to the name
                )

        # Branches
        query_insert_branches(conn, default_branch, repository_id)
        for commit in commit_data:
            query_insert_commits(
                conn,
                commit["sha"],
                commit["commit"]["author"]["date"],
                commit["commit"]["message"],
                commit["commit"]["author"]["name"],
                repository_id,
            )

        # Languages
        lang_names = list(lang_data.keys())
        for lang_name in lang_names:
            lang_name = str(lang_name)
            query_insert_language(conn, repository_id, lang_name)


    # except Exception as e:
    #      exc_type, exc_obj, exc_tb = sys.exc_info()
    #      f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #      print(exc_type, f_name, exc_tb.tb_lineno)
    #      print(f"Error processing repository {owner}/{repo}: {e}")
    finally:
        conn.close()


