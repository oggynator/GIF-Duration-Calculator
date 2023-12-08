import os
from tkinter import Tk, filedialog, Label, Button, Listbox, Scrollbar, PhotoImage, messagebox
from moviepy.editor import VideoFileClip
import concurrent.futures
import threading
import random

class VideoLengthCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Duration Calculator - Version 1.0.0")

        self.file_paths = []
        self.total_length = 0
        self.skipped_files = 0

        self.label = Label(root, text="Vælg GIF filer eller en mappe for at udregne GIF afspilningslængden.")
        self.label.pack(pady=10)

        self.browse_button = Button(root, text="Vælg filer", command=self.browse_files)
        self.browse_button.pack(pady=10)

        self.browse_directory_button = Button(root, text="Vælg mappe", command=self.browse_directory)
        self.browse_directory_button.pack(pady=10)

        self.listbox = Listbox(root, selectmode="multiple", height=5)
        self.listbox.pack(pady=10)

        self.calculate_button = Button(root, text="Udregn afspilningslængde", command=self.calculate_video_length)
        self.calculate_button.pack(pady=10)

        self.loading_label = Label(root, text="")
        self.loading_label.pack(pady=10)

        self.result_label = Label(root, text="")
        self.result_label.pack(pady=10)

    def browse_files(self):
        file_paths = filedialog.askopenfilenames(title="Vælg GIF filer", filetypes=[("GIF files", "*.gif")])
        self.file_paths = list(file_paths)
        self.update_listbox()

    def browse_directory(self):
        directory_path = filedialog.askdirectory(title="Vælg mappe")
        self.file_paths = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if filename.endswith(".gif")]
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, 'end')
        for file_path in self.file_paths:
            self.listbox.insert('end', os.path.basename(file_path))

    def calculate_video_length(self):
        if not self.file_paths:
            self.result_label.config(text="Hey makker, du skal lige vælge filer eller en mappe!")
            return

        # Randomly select a loading message
        loading_messages = [
        "Træner en hamster til at løbe hurtigere på hjulet...",
        "Hidkalder Avengers for at beregne dette for dig...",
        "Finder den manglende sok i serverrummet...",
        "Sætter turbo på koden og håber på det bedste...",
        "Oversætter binært til dansk...",
        "Lærer computeren at danse Macarenaen..."
        ]
        random_message = random.choice(loading_messages)
        self.loading_label.config(text=random_message)

        # Run the video processing in a separate thread
        processing_thread = threading.Thread(target=self.process_video_length)
        processing_thread.start()

    def process_video_length(self):
        total_length = 0
        skipped_files = 0
        num_files = len(self.file_paths)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.process_video_file, self.file_paths))

        for i, (length, skipped) in enumerate(results):
            total_length += length
            skipped_files += skipped
            # You can add a sleep here if the processing is too fast and the loading message disappears quickly
            # time.sleep(0.1)

        self.total_length = total_length
        self.skipped_files = skipped_files

        # Update the GUI in the main thread
        self.root.after(0, self.update_gui)

    def update_gui(self):
        self.loading_label.config(text="")  # Remove loading text

        results_text = f"Samlet afspilningslængde (HH:MM:SS): {self.format_duration(self.total_length)}\n"
        results_text += f"Antal filer som ikke kunne læses: {self.skipped_files}"

        self.result_label.config(text=results_text)

        # Export individual video lengths to a text file
        self.export_to_text_file()

    def process_video_file(self, file_path):
        try:
            clip = VideoFileClip(file_path)
            length = clip.duration
            return length, 0
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return 0, 1

    @staticmethod
    def format_duration(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{seconds:.2f}"

    def export_to_text_file(self):
        if not self.file_paths:
            return

        # Determine the output folder based on the folder of the first selected GIF
        output_folder = os.path.dirname(self.file_paths[0])
        output_file_path = os.path.join(output_folder, "individual_video_lengths.txt")

        with open(output_file_path, "w") as file:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(self.process_and_write_to_file, self.file_paths, [file] * len(self.file_paths)))

            # Add a line for the total video length at the end of the file
            file.write(f"\nTotal GIF Video Length (HH:MM:SS): {self.format_duration(self.total_length)}")

    def process_and_write_to_file(self, file_path, file):
        try:
            clip = VideoFileClip(file_path)
            length = clip.duration
            file.write(f"{os.path.basename(file_path)}: {self.format_duration(length)}\n")
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            file.write(f"{os.path.basename(file_path)}: SKIPPED\n")

if __name__ == "__main__":
    root = Tk()
    calculator = VideoLengthCalculator(root)
    root.mainloop()
