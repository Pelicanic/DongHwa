module.exports = {
  apps: [{
    name: 'runfront',
    script: 'npm',
    args: 'run start',
    cwd: '/d/AI_cjw/DongHwa/front',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};