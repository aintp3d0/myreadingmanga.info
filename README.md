Full-stack web application to track newly added manga

> [!CAUTION]
> Use the branch `start`, `main` is used as a development

> [!NOTE]
> Brief: Downloading Manga Images and Converting them to PDF<br />
> All contributions are very welcome! [TODO](./_data/readme/TODO.md)

<details>
<summary>Start this project</summary>
<pre>
docker -v   # Docker version 27.5.1, build 9f9e405
python -V   # Python 3.12.3
</pre>
</details>

```bash
docker compose up --build -d
```

<details>
<summary>Run CLI without WebUI</summary>
<pre>
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
</pre>
</details>

```bash
python cli.py -h
```
