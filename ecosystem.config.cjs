module.exports = {
  apps: [
    {
      name: 'lynx-dev',
      namespace: 'novia',
      script: 'npx',
      args: 'rspeedy dev',
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: 'development',
      },
    },
    {
      name: 'temporal-server',
      namespace: 'novia',
      script: 'temporal',
      args: 'server start-dev --ui-port 8233',
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: 'development',
      },
    },
    {
      name: 'api-server',
      namespace: 'novia',
      cwd: './backend',
      script: 'bash',
      args: '-c "source .venv/bin/activate && uvicorn src.main:app --reload --port 8000"',
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: 'development',
      },
    },
    {
      name: 'temporal-worker',
      namespace: 'novia',
      cwd: './backend',
      script: 'bash',
      args: '-c "source .venv/bin/activate && python -m src.temporal.worker"',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        NODE_ENV: 'development',
      },
    },
  ],
};
