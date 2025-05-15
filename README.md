# LLVM to MIPS

This repository contains the source for the tutorial series on writing a 
backend for LLVM that compiles to MIPS Release 1 assembly.

This serves as a guide to anyone interested in developing a backend for LLVM.

The name of this backend is `Nova`, just to distinguish from the already existing
`Mips` backend. (Most of the code is derived from that)

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

## Running locally
The code snippets for the pages are extracted and embedded into
the webpage source by reading code enclosed within special
snippet comments in the LLVM source.

This repository has currently checked in the `snippets.json` file
that stores all these extracted snippets, but this might change later.
(in fact, probably *should* change later)

You can skip steps 1 and 4 if you just want to build and develop the 
website content without changing the code for the Nova backend.

1. Clone the llvm-project directory.
```bash
cd llvm-mips-tutorial # or whatever you name this
                      # book-tutorial-project's directory
git clone --single-branch --branch nova-backend https://github.com/optimisan/llvm-project.git
```

2. Clone this repository.
```bash
cd llvm-mips-tutorial
git clone https://github.com/optimisan/llvm-mips-backend.git
```

3. Copy (or move) the `.env.example` to `.env`.
```bash
cd llvm-mips-tutorial/llvm-mips-backend # cd into this project
cp .env.example .env
open_with_editor .env
```

Enter the absolute path to the `llvm-project` folder, for example, like this:
```env
# in file .env
LLVM_ROOT_DIR=/home/username/llvm-mips-tutorial/llvm-project
```

4. Build the snippets. Requires python and the `python-dotenv` package.
```bash
# optional: pip3 install python-dotenv 
./build-snippets
```

5. Build and view the website!
```bash
npm install
npm run dev
```

Open `localhost:4321` in your browser.

## Snippets
Look at [tools/snippet-parser/README.md](tools/snippet-parser/README.md) for the snippets syntax.

## Other stuff that Astro added to this README
| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`      |
| `npm run build`           | Build your production site to `./dist/`          |
| `npm run preview`         | Preview your build locally, before deploying     |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Check out [Starlight’s docs](https://starlight.astro.build/), read [the Astro documentation](https://docs.astro.build), or jump into the [Astro Discord server](https://astro.build/chat).
