#!/usr/bin/env python3
""" Script to report issues from github repository
Depends on PyGithub and requires an exported env var
for Github API access.

Create a virtual environment in the root directory of shop24:

$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ export GITHUB_TOKEN="f41...a9"
(venv) $ python3 github/report_stories.py

"""

import os
from github import Github


def export_issues():
    """ Function to export issues as formatted text

        Obtain token at github https://github.com/settings/tokens
        Save somewhere securely as github will not display it again

        Export token as environment variabe.
        On Linux:
        export GITHUB_TOKEN="f41...a9"
        Then run this script using python 3

        Example of issue API access follows
        customize the format string to taste.

        Try to paste format into submission doc without manual formatting
        use monospace font (defined style exists)

        >>> import os
        >>> from github import Github
        >>> g = Github(os.getenv("GITHUB_TOKEN"))  # access token
        >>> repo = g.get_repo("kowalczj/shop24")
        >>> label_user_story = repo.get_label("user story")
        >>> label_priority_1 = repo.get_label("priority 1")
        >>> issues = repo.get_issues()
        >>> issue = issues[0]
        >>> issue.
        issue.CHECK_AFTER_INIT_FLAG issue.get_timeline(
        issue.active_lock_reason    issue.html_url
        issue.add_to_assignees(     issue.id
        issue.add_to_labels(        issue.labels
        issue.as_pull_request(      issue.labels_url
        issue.assignee              issue.last_modified
        issue.assignees             issue.lock(
        issue.body                  issue.locked
        issue.closed_at             issue.milestone
        issue.closed_by             issue.number
        issue.comments              issue.pull_request
        issue.comments_url          issue.raw_data
        issue.create_comment(       issue.raw_headers
        issue.create_reaction(      issue.remove_from_assignees(
        issue.created_at            issue.remove_from_labels(
        issue.delete_labels(        issue.repository
        issue.edit(                 issue.setCheckAfterInitFlag(
        issue.etag                  issue.set_labels(
        issue.events_url            issue.state
        issue.get__repr__(          issue.title
        issue.get_comment(          issue.unlock(
        issue.get_comments(         issue.update(
        issue.get_events(           issue.updated_at
        issue.get_labels(           issue.url
        issue.get_reactions(        issue.user
        """
    g = Github(os.getenv("GITHUB_TOKEN"))  # access token

    repo = g.get_repo("kowalczj/shop24")

    label_user_story = repo.get_label("user story")
    label_priority_1 = repo.get_label("priority 1")

    for issue in repo.get_issues(
        state="open", direction="desc", labels=[label_user_story,]
    ):
        print(
            "#{}: {}\n{}\n{}\n\n".format(
                issue.number,
                issue.title,
                ", ".join([label.name for label in issue.labels]),
                issue.body,
            )
        )


if __name__ == "__main__":
    export_issues()
