from github import Github
import os
import traceback
from difflib import SequenceMatcher

cwd = os.getcwd()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def report_error_to_repo(bot, thrown):
    access_token = ""

    print(str(thrown))

    with open(cwd + '/git/git_access_token.txt', 'r') as myfile:
        access_token = myfile.read()

    try:
        g = Github(access_token)
        repo = g.get_repo("joeShuff/discord-RPGSteveBot")
        bot_label = repo.get_label("bot reported issue")

        thrown_issue = ''.join(traceback.format_exception(etype=type(thrown), value=thrown, tb=thrown.__traceback__))
        report = "Error collected from " + str(bot.user.name) + "\n```" + thrown_issue + "```"

        all_issues = repo.get_issues()

        alreadyReported = None

        for issue in all_issues:
            if similar(issue.body, report) > 0.95:
                alreadyReported = issue
                issue.create_comment(body="+1\n\n" + report)

        if alreadyReported is not None:
            print("+1d existing issue")
            return alreadyReported

        issue = repo.create_issue(
            title="Error from Bot",
            body=report,
            labels=[bot_label],
            assignee="joeShuff"
        )

        print("Reported error to github")
        return issue
    except:
        return None
