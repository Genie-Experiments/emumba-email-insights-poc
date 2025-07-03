# emumba Email Insights

emumba Email Insights is a web application designed to provide AI-powered insights from email conversations. This project uses React, TypeScript, and Vite for the frontend, and Docker for deployment.

## Table of Contents

- [Installation](#installation)
- [Development](#development)
- [Building](#building)
- [Running](#running)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

## Installation

1. **Clone the repository:**

```sh
git clone https://github.com/your-repo/emumba-email-insights.git
cd emumba-email-insights
```

2. **Install dependencies:**

```sh
npm install
```

## Development

To start the development server with hot module replacement:

```sh
npm run dev
```

This will start the Vite development server on http://localhost:3000.

## Building

To build the project for production:

```sh
npm run build
```

The built files will be output to the `dist` directory.

## Running

To preview the production build locally:

```sh
npm run preview
```

This will start a local server to serve the built files.

## Deployment

### Docker

1. **Build the Docker image:**

```shell
docker build -t emumba-email-insights .
```

2. **Run the docker container:**

```shell
docker run -p 8501:8501 emumba-email-insights
```

The application will be available at http://localhost:8501.

## GitHub Actions

This project uses GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/ci-workflow.yaml`.

The workflow will:

1. Build and push the Docker image to GitHub Container Registry on every push to the `dev` branch or when a pull request to `dev` is merged.
2. Use the current date, branch name, and commit ID to tag the Docker image.

## Project Structure

```
.github/
  workflows/
   ci-workflow.yaml
.gitignore
Dockerfile
eslint.config.js
index.html
nginx.conf
package.json
public/
README.md
src/
  api/
   axiosInstance.ts
   fetchCompanyNames.ts
   generate.ts
  App.tsx
  assets/
  components/
   attachmentModal/
   emailAttachments/
   emailModal/
   emailTags/
   footer/
   gptQueryForm/
   gptQueryForm2/
   ...
  data/
   questions.ts
  index.css
  main.tsx
  pages/
   ...
  types/
  utils/
  vite-env.d.ts
tsconfig.app.json
tsconfig.json
tsconfig.node.json
vite.config.ts
```

## Key Files and Directories:

- `src/`: Contains the source code for the application.
- `api/`: API integration files.
- `components/`: React components.
- `data/`: Static data files.
- `pages/`: Page components.
- `utils/`: Utility functions.
- `Dockerfile`: Docker configuration for building and running the application.
- `nginx.conf`: Nginx configuration for serving the application.
- `package.json`: Project metadata and dependencies.
- `tsconfig.json`: TypeScript configuration.
