var numSelected = null;
var tileSelected = null; // Fixed typo: renamed 'titleSelected' to match conventions

var errors = 0;

var board = [
    "--74916-5",
    "2---6-3-9",
    "-----7-1-",
    "-586----4",
    "--3----9-",
    "--62--187",
    "9-4-7---2",
    "47-83----",
    "81--45---"
];

var solution = [
    "387491625",
    "241568379",
    "569327418",
    "358419234",
    "132874596",
    "496253187",
    "934171452",
    "675872941",
    "812945763"
];

window.onload = function() {
    setGame();
}

function setGame() {
    // 1. Set up event listeners for the numbers already inside your HTML
    for (let i = 1; i <= 9; i++) {
        let number = document.getElementById(i.toString());
        if (number) {
            number.addEventListener("click", selectNumber);
        }
    } 

    // 2. MOVED INSIDE setGame: Generate the 81 grid tiles dynamically
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            let tile = document.createElement("div");
            tile.id = r.toString() + "-" + c.toString();
            
            // Set tile values properly without printing '-' characters
            if (board[r][c] != "-") {
                tile.innerText = board[r][c];
                tile.classList.add("tile-start");
            } else {
                tile.innerText = ""; // Leave blank spaces empty
            }
            
            // Apply grid styling lines
            if (r == 2 || r == 5) {
                tile.classList.add("horizontal-line");
            }
            if (c == 2 || c == 5) {
                tile.classList.add("vertical-line");
            }
            
            tile.classList.add("tile");
            tile.addEventListener("click", selectTile); // Fixed case sensitivity
            document.getElementById("board").appendChild(tile);
        }
    }
}

function selectNumber() {
    if (numSelected != null) {
        numSelected.classList.remove("number-selected");
    }
    numSelected = this;
    numSelected.classList.add("number-selected");
}

// Fixed function name casing to match the event listener (selectTile)
function selectTile() {
    if (numSelected) {
        // Check if tile is empty (not filled by start or a previous correct answer)
        if (this.innerText != "") {
            return;
        }
        
        // Target coordinates from the ID (ex: "0-2" splits into ["0", "2"])
        let coords = this.id.split("-"); // Fixed: split by '-' instead of '='
        let r = parseInt(coords[0]);
        let c = parseInt(coords[1]); // Fixed: missing 's' in coords

        // Validate choice against the solution array
        if (solution[r][c] == numSelected.id) {
            this.innerText = numSelected.id;
        } else {
            errors += 1;
            document.getElementById("errors").innerText = "Error: " + errors;
        }
    }
}
