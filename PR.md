# Rules

Few and simple but mandatory rules.

1. Run the command `make create-module NAME=YOUR_MODULE_NAME` to create a directory with the name of your module
The setup will automatically create the necessary files.
2. Update `main.py`, adding the newly created module to the list `all_modules`
3. Take a look at one of the already available modules, for example [postgre](postgre), to understand how to set up everything
4. Do not update [workflows](.github/workflows/), they will eventually be updated by the mainteiner
5. All produced code must pass `make lint` directives, and make sure to also run `make format` to try to solve some linting problems automatically
6. Do not expect merges even if everything is fine; compilation times and size of compiled binaries will be taken into consideration.
7. Builds must be succesfull, mainteiner will check the code but not update/change it.