<p align="center">
  <pre>
   _                                  
  | |                                 
  | | __ _ _____   _ _ __ _   _ _ __  
  | |/ _` |_  / | | | '__| | | | '_ \ 
  | | (_| |/ /| |_| | |  | |_| | | | |
  |_|\__,_/___|\__, |_|   \__,_|_| |_|
                 __/ |                 
                |___/                  
  </pre>
</p>

<h1 align="center">🚀 lazyrun</h1>
<p align="center"><strong>Task Runner With Memory</strong></p>
<p align="center">Save and run your most-used shell commands as one-word shortcuts!</p>

---

## 🧩 Features

- **Save** any shell command under a custom name  
- **Run** it later with `lazyrun <name>`  
- **Fuzzy-match** & typo-correction via [snaparg](https://github.com/ArchooD2/snaparg)  
- **Cross-platform** config directory (Windows/macOS/Linux)  
- **Zero dependencies** beyond Python, snaparg & AppDirs  

---

## 🚀 Quickstart

```bash
# 1) Install
pip install lazyrun

# 2) Save your first shortcut
lazyrun save build "python setup.py sdist bdist_wheel"

# 3) Run it any time
lazyrun build
```

---

## 📖 Usage

### Save a shortcut

```bash
lazyrun save <name> "<full shell command>"
```

### List all shortcuts

```bash
lazyrun list
```

### Remove a shortcut

```bash
lazyrun remove <name>
```

### Run a shortcut

```bash
lazyrun <name>
```

---

## ⚙️ Configuration

Shortcuts are stored in JSON at:

- **Windows:** `%LOCALAPPDATA%\lazyrun\config.json`  
- **macOS/Linux:** `~/.config/lazyrun/config.json`  

No manual setup needed—lazyrun creates the folder & file on first run.

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch: `git checkout -b feature/awesome`  
3. Commit your changes & push: `git push origin feature/awesome`  
4. Open a Pull Request  

All contributions welcome! 🛠️

---

## 📄 License

Distributed under the [Mozilla Public License 2.0](https://www.mozilla.org/en-US/MPL/2.0/).
