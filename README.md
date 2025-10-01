# BFF-Demo
### Prerequisites
- Docker
- Nix Package Manager (with Flakes)

### Install Nix CLI
The quickest way to have a great Nix experience is with [Determinate Systems](https://determinate.systems/blog/determinate-nix-installer/). This one liner will do just that on any supported system:
```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```
## devShell
The devShell is a Nix environment that contains all the dependencies needed to run the project. It's a great way to ensure that everyone working on the project has the same dependencies and the same versions of those dependencies. ( works best with bash terminal )
#### See what's available
```bash
nix flake show --all-systems
```
#### Enter the devShell
It's best practice to enter the devShell then run VSCode from the devShell. But not required.
```bash
nix develop
```
#### FastAPI Hot Reload
```bash
nix run
```
This launches 6 terminals in tmux: TailwindCSS CLI watcher, Lazydocker for inspecting Docker things, MongoDB with pretty logs, MongoDB-Compass for interacting with MongoDB, Chrome with DevTools, FastAPI hot reload server.
#### Docker Container
```bash
nix run .#container
```
#### Docker Container Attached
```bash
nix run .#container-attached
```
#### Docker Compose
```bash
nix run .#docker-compose
```
#### Pytest Coverage
```bash
nix run .#pytest-cov
```
### Build the App
```bash
nix build
```
### Build Docker Image
```bash
nix build .#bff-demo-container
```
### Check the flake.nix
```bash
nix flake check --all-systems
```
This will check the `flake.nix` syntax and that all the dependencies are pinned. Also will run `pyrefly` the Facebook Python type checker, `ruff` the Python linter, and `pytest` the Python test runner.