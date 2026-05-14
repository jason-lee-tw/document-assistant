# Repo restructuring

This repo is going to have multiple sub-repo in @apps/ folder such as backend (the current Python application) and frontend (a React app gonna to be implemented later on).
However, with the current structure, it is hard to extend to multiple repo.

## Current architecture

There is a backend application in @src/ and dockerized with dockerfiles in @docker/ .
The starting up of the project is running commands in @Justfile .
There are postgres vector db and phoenix running and integrated with the backend application.

## Constraints

- The scripts in @scripts/ MUST NOT be moved.
- The documents in @docs/ MUST NOT be moved.
- The @sample-docs/ folder can be moved into backend folder.
- UV configuration files can be moved into the backend folder.
- Make the main repo to hold the `.venv`. (I guess it should be using workspace?)
- Should make the changes as simple as possible.
- NEVER make any assumption. Always clarify if there is anything unclear.
- ALWAYS plan before start implementing.

## Your Task

You are tasked to restructure this repo.
Explore and understand the current project configuration and structure first.
