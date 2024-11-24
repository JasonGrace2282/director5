(ide-setup)=

# Setting up your IDE of choice

## Tailwind

Tailwindcss is used to style all webpages, and the development process is much easier
when you have an autocomplete plugin installed.

```{note}
Most IDEs have community-made or first-party supported plugins that do not require the project to have NodeJS.
If that is the case for your IDE (i.e. VSCode) then you can skip this section
```

Because we rely on Tailwind's individual CLI instead of its node version, some plugins
that rely on NodeJS to be installed in the project, such as PyCharm's Tailwind plugin, won't function correctly.

To fix this, on your local machine, run the following commands to install a 'dummy version' of node tailwind
(requires [NodeJS](https://nodejs.org/en/download/package-manager) to be installed locally)

```bash
cd dev/tailwind
./enable-pycharm-autocomplete.sh
```

Check to make sure a `pyc-autocomplete` folder was created within `dev/tailwind`, and that it contains `tailwind.config.js`,
`node_modules`, `package.json`, and `package-lock.json`

Finally, restart your IDE. If you're on PyCharm, ensure that the `node_modules` folder is marked as `library root`
