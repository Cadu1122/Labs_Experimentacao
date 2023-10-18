from datetime import date, datetime
from typing import TypeVar, TypedDict

from lch.modules.questions.question_1.models.repository import Repository
from lch.shared.date_shared import diff_in_days, diff_in_hours

Language = TypeVar('Language', bound=str)
NumberOfRepositories = TypeVar('NumberOfRepositories', bound=int)

class RepositoryAnalysisObject(TypedDict):
    ages: list[int]
    stars_and_ages: list[int, int]

    accepted_prs: list[int]
    stars_and_accepted_prs: list[list[int, int]]

    total_of_releases: list[int]
    stars_and_total_of_releases: list[list[int, int]]

    update_frequency: list[int]
    stars_and_update_frequency: list[list[int, int]]

    percent_of_closed_issues: list[int]
    stars_and_percent_of_closed_issues: list[list[int, int]]

    languages: dict[Language, NumberOfRepositories]

def get_analysis_object_from_repositories(repositories: list[Repository]):
        today = date.today()
        now = datetime.now()
        analysis_object: RepositoryAnalysisObject = {
            'ages': [],
            'stars_and_ages': [[], []],
            'accepted_prs': [],
            'stars_and_accepted_prs': [[], []],
            'total_of_releases': [],
            'stars_and_total_of_releases': [[], []],
            'update_frequency': [],
            'stars_and_update_frequency': [[], []],
            'percent_of_closed_issues': [],
            'stars_and_percent_of_closed_issues': [[], []],
            'languages': {},
        }
        for repository in repositories:
            
            stars = repository.get('stars')
            age = diff_in_days(today, repository.get('created_at'))
            accepted_prs = repository.get('merged_prs')
            total_of_releases = repository.get('total_of_releases')
            total_of_issues = repository.get('total_of_issues')

            analysis_object['ages'].append(age)
            analysis_object['stars_and_ages'].append([age, stars])

            analysis_object['accepted_prs'].append(accepted_prs)
            analysis_object['stars_and_accepted_prs'].append([accepted_prs, stars])

            analysis_object['total_of_releases'].append(total_of_releases)
            analysis_object['stars_and_total_of_releases'].append([total_of_releases, stars])

            if total_of_issues:
                percent = repository.get('closed_issues') / total_of_issues
                analysis_object['percent_of_closed_issues'].append(percent)
                analysis_object['stars_and_percent_of_closed_issues'].append([percent, stars])
            if repository.get('last_update_date'):
                last_release = diff_in_hours(now, repository.get('last_update_date'))
                analysis_object['update_frequency'].append(last_release)
                analysis_object['stars_and_update_frequency'].append([last_release, stars])
            language = repository.get('primary_language')
            if analysis_object['languages'].get(language):
                 analysis_object['languages'][language] +=1
            else:
                 analysis_object['languages'][language] = 1
        return analysis_object