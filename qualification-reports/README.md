# Qualification Reports

This directory is mounted into the Climate Bridge container at `/reports`.

Generated qualification reports are written here so they remain available on
the host after the container is rebuilt or replaced.

The directory is intentionally included in every release package because
`docker-compose.yml` references it as a bind-mount source.
