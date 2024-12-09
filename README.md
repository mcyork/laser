# Laser Maze Project

## Development Setup

1. Ensure Python 3.x is installed
2. Run setup script: `./setup-dev.sh`
3. Activate virtual environment: `source .venv/bin/activate`
4. Run development server: `python run.py`

## Project Structure

```
laser_maze/
├── app/                    # Application package
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── static/            # Static files
│   └── templates/         # Jinja2 templates
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── .env                   # Environment variables
├── config.py             # Configuration
└── run.py                # Application entry point
```

## Deployment

To deploy to the Raspberry Pi:
1. Commit your changes
2. Run `scripts/deploy.sh`
