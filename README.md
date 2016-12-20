# FormosaMatch

## Description

Final project for Advanced Databases Master's Course - NTHU 2016



## Disclaimer
This Docker setup was done using the following links for inspiration

https://github.com/DBProductions/neo4j-flask
https://realpython.com/blog/python/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/

## Instructions - WOW!

We can use Docker for our developing infrastructure

If messing around with too many containers, try out

https://github.com/ZZROTDesign/docker-clean

	docker-clean stop
	docker-clean images

These commands will clean up your docker :)

To build our Flask+Neo4j environment, run:

	docker-compose build

And then:

	docker-compose up

The website will be available on localhost and the Neo4j panel on localhost:7474.
