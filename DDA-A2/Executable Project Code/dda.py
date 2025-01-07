# Import necessary modules for GUI, web requests, and handling images
import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas
from PIL import Image, ImageTk  # For handling images and converting them for use in Tkinter
import requests  # To fetch data from the API
import io  # To handle byte data
import webbrowser  # To open URLs in the browser

# API key and base URL for The Movie Database API
API_KEY = "94c7237d30c21075165bdebd992da2ad"
BASE_URL = "https://api.themoviedb.org/3"

# Main class for the movie app
class MovieApp:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("Movie Explorer")  # Set the window title
        self.root.geometry("930x800")  # Set the size of the window
        self.dark_mode = False  # For future dark mode feature (not implemented here)
        self.favorites = []  # List to store favorite movies

        # Set the background color for the window
        self.root.configure(bg="#1a1a1a")

        # Add the title at the top
        self.title_label = tk.Label(root, text="🎥 Movie Explorer 🎥", font=("Arial", 24, "bold"), bg="#0f0f0f", fg="#00ffaa", pady=10)
        self.title_label.pack(fill=tk.X)

        # Create a frame for filter and search options
        filter_frame = tk.Frame(root, bg="#1a1a1a")
        filter_frame.pack(fill=tk.X, pady=10)

        # Add buttons for various actions like Random Movie, Filter, Popular, Search, and Favorites
        random_btn = self.styled_button(filter_frame, "Random Movie", self.display_random_movie)
        random_btn.pack(side=tk.LEFT, padx=5)

        genre_btn = self.styled_button(filter_frame, "Filter by Genre", self.filter_by_genre)
        genre_btn.pack(side=tk.LEFT, padx=5)

        popular_btn = self.styled_button(filter_frame, "Popular Movies", self.display_popular_movies)
        popular_btn.pack(side=tk.LEFT, padx=5)

        # Add a search box for typing queries
        self.search_entry = tk.Entry(filter_frame, width=30, bg="#2c2c2c", fg="#ffffff", insertbackground="#ffffff", font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Add a search button next to the search box
        search_btn = self.styled_button(filter_frame, "Search", lambda: self.search_movie(self.search_entry.get()))
        search_btn.pack(side=tk.LEFT, padx=5)

        # Add a button to view the list of favorite movies
        favorites_btn = self.styled_button(filter_frame, "View Favorites", self.show_favorites)
        favorites_btn.pack(side=tk.LEFT, padx=5)

        # Back button to return to the latest movies
        self.back_btn = self.styled_button(root, "Back", self.get_latest_movies)
        self.back_btn.pack(pady=10)

        # Add a label for the section heading (Latest Movies by default)
        self.movie_heading = tk.Label(root, text="✨ Latest Movies ✨", font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#ffcc00")
        self.movie_heading.pack(pady=10)

        # Create a scrollable container to display movies
        self.canvas = Canvas(root, bg="#1a1a1a", highlightthickness=0)
        self.scroll_y = Scrollbar(root, orient="vertical", command=self.canvas.yview, bg="#1a1a1a")
        self.movie_frame = tk.Frame(self.canvas, bg="#1a1a1a")

        # Adjust the scrollable area when the content changes
        self.movie_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Add the movie frame inside the canvas
        self.canvas.create_window((0, 0), window=self.movie_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Pack the scrollbar and the canvas
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        # Display the latest movies on app start
        self.get_latest_movies()

    def styled_button(self, parent, text, command):
        """Create a button with custom styling and hover effects."""
        btn = tk.Button(parent, text=text, font=("Arial", 10, "bold"), bg="#0f0f0f", fg="#00ffaa", activebackground="#00ffaa", activeforeground="#0f0f0f", bd=0, pady=5, padx=10, command=command)
        # Change the button color when the mouse hovers over it
        btn.bind("<Enter>", lambda e: btn.config(bg="#00ffaa", fg="#0f0f0f"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#0f0f0f", fg="#00ffaa"))
        return btn

    def api_request(self, endpoint, params={}):
        """Make a request to the movie API and handle errors."""
        params["api_key"] = API_KEY  # Add the API key to the request parameters
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        if response.status_code == 200:  # If the request is successful
            return response.json()  # Return the JSON response
        else:
            # Show an error if the request fails
            messagebox.showerror("Error", f"Failed to fetch data: {response.status_code}")
            return None

    def get_latest_movies(self):
        """Fetch and display the latest movies."""
        self.movie_heading.config(text="✨ Latest Movies ✨")  # Update heading
        data = self.api_request("/movie/now_playing", {"language": "en-US", "page": 1})
        if data:  # If data is retrieved successfully
            self.display_movies(data["results"])  # Display the movies

    def display_random_movie(self):
        """Pick and display a random movie from popular ones."""
        self.movie_heading.config(text="🎲 Random Movie 🎲")  # Update heading
        data = self.api_request("/movie/popular", {"language": "en-US", "page": 1})
        if data:
            import random  # Import random for picking a movie
            random_movie = random.choice(data["results"])  # Pick one randomly
            self.display_movies([random_movie])  # Display the random movie

    def display_popular_movies(self):
        """Fetch and display popular movies."""
        self.movie_heading.config(text="⭐ Popular Movies ⭐")  # Update heading
        data = self.api_request("/movie/popular", {"language": "en-US", "page": 1})
        if data:
            self.display_movies(data["results"])  # Display the movies

    def search_movie(self, query):
        """Search for a movie based on the user input."""
        if not query.strip():  # Check if the search box is empty
            messagebox.showwarning("Warning", "Please enter a search query!")
            return
        self.movie_heading.config(text=f"🔍 Search Results for '{query}' 🔍")  # Update heading
        data = self.api_request("/search/movie", {"query": query, "language": "en-US"})
        if data:
            self.display_movies(data["results"])  # Display the search results

    def filter_by_genre(self):
        """Filter movies by genre."""
        data = self.api_request("/genre/movie/list", {"language": "en-US"})
        if data:  # If genres are fetched successfully
            genres = data.get("genres", [])  # Get the list of genres
            genre_map = {genre["name"]: genre["id"] for genre in genres}  # Map genre names to IDs

            def select_genre():
                selected_genre = genre_var.get()  # Get the selected genre
                genre_id = genre_map.get(selected_genre)  # Get its ID
                if genre_id:
                    self.movie_heading.config(text=f"🎭 Movies in {selected_genre} 🎭")  # Update heading
                    movies = self.api_request("/discover/movie", {"with_genres": genre_id, "language": "en-US"})
                    if movies:
                        self.display_movies(movies.get("results", []))  # Display movies in the selected genre

            # Create a new window to show the list of genres
            genre_window = tk.Toplevel(self.root)
            genre_window.title("Select Genre")
            genre_var = tk.StringVar(genre_window)  # Variable to hold the selected genre
            genre_var.set(next(iter(genre_map.keys()), ""))  # Set the default value
            genre_menu = tk.OptionMenu(genre_window, genre_var, *genre_map.keys())  # Dropdown menu for genres
            genre_menu.pack(pady=10)

            # Add a button to filter by the selected genre
            select_btn = tk.Button(genre_window, text="Filter", command=lambda: [select_genre(), genre_window.destroy()])
            select_btn.pack(pady=5)

    def display_movies(self, movies):
        """Show movies in the movie frame."""
        # Clear existing movie cards
        for widget in self.movie_frame.winfo_children():
            widget.destroy()

        # Loop through the movies and create cards for each one
        for index, movie in enumerate(movies):
            poster_url = f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie['poster_path'] else None
            movie_card = tk.Frame(self.movie_frame, bg="#0f0f0f", bd=2, relief=tk.GROOVE)
            movie_card.grid(row=index // 6, column=index % 6, padx=10, pady=10)

            if poster_url:  # If the movie has a poster
                image_data = requests.get(poster_url, stream=True).content  # Fetch the image data
                image = Image.open(io.BytesIO(image_data))  # Open the image
                image = image.resize((120, 180), Image.Resampling.LANCZOS)  # Resize the image
                photo = ImageTk.PhotoImage(image)  # Convert it to a format Tkinter can use

                poster_label = tk.Label(movie_card, image=photo, bg="#0f0f0f")  # Create an image label
                poster_label.image = photo  # Keep a reference to prevent garbage collection
                poster_label.pack(pady=5)

            # Add the movie title
            title_label = tk.Label(movie_card, text=movie["title"], wraplength=100, bg="#0f0f0f", fg="#00ffaa", font=("Arial", 10, "bold"))
            title_label.pack(pady=5)

            # Add buttons for actions like adding to favorites, watching the trailer, and viewing details
            favorite_btn = self.styled_button(movie_card, "Add to Favorites", lambda m=movie: self.add_to_favorites(m))
            favorite_btn.pack(pady=5)

            trailer_btn = self.styled_button(movie_card, "Watch Trailer", lambda m=movie: self.watch_trailer(m))
            trailer_btn.pack(pady=5)

            details_btn = self.styled_button(movie_card, "Details", lambda m=movie: self.show_details(m))
            details_btn.pack(pady=5)

    def add_to_favorites(self, movie):
        """Add a movie to the favorites list."""
        if movie not in self.favorites:  # Check if the movie is already in favorites
            self.favorites.append(movie)  # Add to favorites
            messagebox.showinfo("Favorites", f"{movie['title']} added to favorites!")
        else:
            messagebox.showinfo("Favorites", f"{movie['title']} is already in favorites!")

    def show_favorites(self):
        """Display favorite movies in a new window."""
        if not self.favorites:  # If there are no favorites
            messagebox.showinfo("Favorites", "No favorite movies added yet!")
            return

        # Create a new window to show favorite movies
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Favorite Movies")
        favorites_window.geometry("700x600")
        favorites_window.configure(bg="#1a1a1a")

        # Title for the favorites section
        title_label = tk.Label(favorites_window, text="❤️ Favorite Movies ❤️", font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#ffcc00")
        title_label.pack(pady=10)

        # Scrollable area for favorite movies
        canvas = Canvas(favorites_window, bg="#1a1a1a", highlightthickness=0)
        scroll_y = Scrollbar(favorites_window, orient="vertical", command=canvas.yview, bg="#1a1a1a")
        fav_frame = tk.Frame(canvas, bg="#1a1a1a")

        fav_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Add the favorite frame inside the canvas
        canvas.create_window((0, 0), window=fav_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        # Display the favorite movies in a grid
        for index, movie in enumerate(self.favorites):
            poster_url = f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie['poster_path'] else None
            movie_card = tk.Frame(fav_frame, bg="#0f0f0f", bd=2, relief=tk.GROOVE)
            movie_card.grid(row=index // 3, column=index % 3, padx=10, pady=10)

            if poster_url:
                image_data = requests.get(poster_url, stream=True).content
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((120, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                poster_label = tk.Label(movie_card, image=photo, bg="#0f0f0f")
                poster_label.image = photo
                poster_label.pack(pady=5)

            title_label = tk.Label(movie_card, text=movie["title"], wraplength=100, bg="#0f0f0f", fg="#00ffaa", font=("Arial", 10, "bold"))
            title_label.pack(pady=5)

            remove_btn = self.styled_button(movie_card, "Remove", lambda m=movie: self.remove_from_favorites(m))
            remove_btn.pack(pady=5)

    def remove_from_favorites(self, movie):
        """Remove a movie from the favorites list."""
        if movie in self.favorites:  # If the movie is in favorites
            self.favorites.remove(movie)  # Remove it
            messagebox.showinfo("Favorites", f"{movie['title']} removed from favorites!")
        else:
            messagebox.showinfo("Favorites", f"{movie['title']} is not in favorites!")

    def watch_trailer(self, movie):
        """Open the trailer link in the browser."""
        movie_id = movie["id"]  # Get the movie ID
        data = self.api_request(f"/movie/{movie_id}/videos", {"language": "en-US"})
        if data:
            results = data.get("results", [])
            # Find a YouTube trailer in the results
            trailer = next((item for item in results if item["site"] == "YouTube" and item["type"] == "Trailer"), None)
            if trailer:
                # Open the YouTube link in the default browser
                webbrowser.open(f"https://www.youtube.com/watch?v={trailer['key']}")
            else:
                # Show a message if no trailer is found
                messagebox.showinfo("Trailer", "No trailer found for this movie!")

    def show_details(self, movie):
        """Display detailed information about a movie."""
        movie_id = movie["id"]  # Get the movie ID
        data = self.api_request(f"/movie/{movie_id}", {"language": "en-US"})
        if data:
            # Create a new window for the details
            details_window = tk.Toplevel(self.root)
            details_window.title(movie["title"])
            details_window.geometry("600x600")
            details_window.configure(bg="#1a1a1a")

            # Add the movie title
            title_label = tk.Label(details_window, text=movie["title"], font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#ffcc00")
            title_label.pack(pady=10)

            # Add the poster if available
            poster_url = f"https://image.tmdb.org/t/p/w300{movie['poster_path']}" if movie['poster_path'] else None
            if poster_url:
                image_data = requests.get(poster_url, stream=True).content
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((200, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                poster_label = tk.Label(details_window, image=photo, bg="#1a1a1a")
                poster_label.image = photo
                poster_label.pack(pady=10)

            # Add the overview
            overview_label = tk.Label(details_window, text=data.get("overview", "No overview available."), wraplength=550, bg="#1a1a1a", fg="#ffffff", font=("Arial", 12))
            overview_label.pack(pady=10)

            # Add additional details like release date, runtime, and rating
            details_text = f"Release Date: {data.get('release_date', 'N/A')}\nRuntime: {data.get('runtime', 'N/A')} minutes\nRating: {data.get('vote_average', 'N/A')} / 10"
            details_label = tk.Label(details_window, text=details_text, bg="#1a1a1a", fg="#ffffff", font=("Arial", 12))
            details_label.pack(pady=10)

# Create the main Tkinter window and start the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()
