# Challenge 1A

Very basic setup to extract outline structure + guessed title from PDF files. Outputs a JSON file per PDF.

## How to Use

Just build it:
```
docker build --platform linux/amd64 -t challenge1a:mogus .
```

Then run it (Make folder `input/` with PDFs in the current directory):
```
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1a:mogus
```

## Output

Each PDF gets a `.json` file in `output/` with:
- `"title"`: best guess at document title (if found)
- `"outline"`: list of heading-ish things, kind of sorted
