#!/usr/bin/env python
""" db queries """

from datetime import datetime

def date():
    """ get formated date """
    return datetime.now().strftime('%F')

"""
  Example of a querie in CYPHER
  See other projects for more examples
"""
def get_all_languages(graph, email):
    """ get all languages of a specific user """
    query = """
    MATCH (language:Language),
          (user:User)
    WHERE NOT (language:Language)<-[:USE]-(user:User)
    AND user.email = {email}
    RETURN language.id as id,
           language.name as name
    """

    return graph.cypher.execute(query, email=email)
