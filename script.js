const API_URL = "http://127.0.0.1:5000/api/games";

const collectionList = document.getElementById("collection_list");
const emptyMessage = document.getElementById("empty_list_msg");

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

            collectionList.append(item)
        }
    } catch (error) {
        console.error("Could not load games:", error);
        emptyMessage.textContent = "Could not load games. Check that the API server is running.";
        emptyMessage.hidden = false;
    }
    
}

loadGames();

const gameForm = document.getElementById("game_form");

gameForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(gameForm);
    const ratingValue = formData.get("rating");

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
        const response = await fetch(API_URL, {
            method: "POST",
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