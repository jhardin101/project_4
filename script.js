const API_URL = "http://127.0.0.1:5000/api/games";

const collectionList = document.getElementById("collection_list");
const emptyMessage = document.getElementById("empty_list_msg");
const gameForm = document.getElementById("game_form");

let editingGameId = null;

const formHeading = document.getElementById("form_heading");
const submitButton = document.getElementById("submit_button");

async function loadGames() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const games = await response.json();

        collectionList.replaceChildren();
        emptyMessage.hidden = games.length > 0;

        for (const game of games) {
            const item = document.createElement("li");
            const title = document.createElement("strong");
            title.textContent = game.title;

            const details = document.createElement("p");
            details.textContent = `${game.platform} - ${game.genre} - ${game.status}`;

            item.append(title, details);

            // Delete Button
            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", async () => {
                if (!confirm(`Delete "${game.title}"?`)) {
                    return;
                }

                try {
                    const response = await fetch(`${API_URL}/${game.id}`, {method: "DELETE"});

                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}`);
                    }

                    await loadGames();
                } catch (error) {
                    console.error("Could not delete game:", error);
                    alert(`Could not delete game: ${error.message}`);
                }
            });

            item.append(deleteButton);

            // Edit Button
            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.textContent = "Edit";

            editButton.addEventListener("click", () => {
                editingGameId = game.id;

                gameForm.elements.title.value = game.title;
                gameForm.elements.platform.value = game.platform;
                gameForm.elements.genre.value = game.genre;
                gameForm.elements.release_year.value = game.release_year;
                gameForm.elements.status.value = game.status;
                gameForm.elements.rating.value = game.rating ?? "";
                gameForm.elements.notes.value = game.notes ?? "";

                formHeading.textContent = "Edit Game";
                submitButton.value = "Save Changes";
                gameForm.scrollIntoView({behavior: "smooth"});
            });
            item.append(editButton);

            collectionList.append(item)
        }
    } catch (error) {
        console.error("Could not load games:", error);
        emptyMessage.textContent = "Could not load games. Check that the API server is running.";
        emptyMessage.hidden = false;
    }
    
}

loadGames();



gameForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(gameForm);
    const ratingValue = formData.get("rating");
    const isEditing = editingGameId !== null;
    const method = isEditing ? "PUT" : "POST";
    const url = isEditing ? `${API_URL}/${editingGameId}` : API_URL;

    const newGame = {
        title: formData.get("title"),
        platform: formData.get("platform"),
        genre: formData.get("genre"),
        release_year: Number(formData.get("release_year")),
        status: formData.get("status"),
        rating: ratingValue === "" ? null : Number(ratingValue),
        notes: formData.get("notes")
    };

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type":"application/json"
            },
            body: JSON.stringify(newGame)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `Server returned ${response.status}`);
        }

        gameForm.reset();
        await loadGames();
    } catch (error) {
        console.error("Could not create game:", error);
        alert(`Could not create game: ${error.message}`);
    }
});

gameForm.addEventListener("reset", async (event) => {
    editingGameId = null;
    formHeading.textContent = "Add a New Game";
    submitButton.value = "Add Game";
})