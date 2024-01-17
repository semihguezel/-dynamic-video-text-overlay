from cv2 import cv2


class VideoProcessor:
    """
    A class for processing a video by adding dynamic text to each frame.

    Attributes:
        video_properties (dict): Dictionary containing video properties (input_path, output_path, width, height).
        text_array (list): List of strings containing the text to be displayed in the video.
        cap: Video capture object.
        total_frame_count (int): Total number of frames in the input video.
        fourcc: VideoWriter fourcc codec.
        out: VideoWriter object.
        text_display_timer_on_screen (dict): Dictionary to store the display time for each text.
        display_counter (int): Counter for tracking the current display time.
        display_index (int): Index to iterate through the text_array.
    """
    def __init__(self, video_properties, text_array):
        """
        Initialize the VideoProcessor with video properties and an array of text to display.

        Args:
            video_properties (dict): Dictionary containing video properties (input_path, output_path, width, height).
            text_array (list): List of strings containing the text to be displayed in the video.
        """
        self.video_properties = video_properties
        self.text_array = text_array

        self.cap = cv2.VideoCapture(self.video_properties['input_path'])
        self.total_frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec based on your needs
        self.out = None

        self.text_display_timer_on_screen = {}
        self.display_counter = 0
        self.display_index = 0

    @staticmethod
    def add_custom_text_to_center(frame, text, image_width, image_height,
                                  font=cv2.FONT_HERSHEY_TRIPLEX, font_scale=1.25,
                                  text_color=(255, 255, 255), thickness=3, outline_color=(0, 0, 0),
                                  line_spacing=20):
        """
        Adds custom text to a frame with specified outline color.

        Parameters:
        - frame: The frame to add text on.
        - text: The text to be placed on the frame.
        - image_width: Width of the frame.
        - image_height: Height of the frame.
        - font: Font type (e.g., cv2.FONT_HERSHEY_SIMPLEX).
        - font_scale: Font scale factor.
        - text_color: Text color (BGR format).
        - thickness: Thickness of the text.
        - outline_color: Outline color (BGR format).
        - line_spacing: Spacing between lines when '\n' is present in the text.

        Returns:
        - The frame with added text.
        """
        lines = text.split("\n")  # '\n' karakterinden itibaren metni ayır

        # Başlangıç yüksekliği hesapla
        y_position = int(
            (image_height + sum([cv2.getTextSize(line, font, font_scale, thickness)[0][1] for line in lines])) / 2) - (
                             cv2.getTextSize(lines[0], font, font_scale, thickness)[0][1] + line_spacing) * len(
            lines) / 2

        # Her satırı yerleştir
        for line in lines:
            (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)

            # Text'ı yerleştirme koordinatlarını hesapla
            x_position = int((image_width - text_width) / 2)
            position = (x_position, int(y_position))

            # Dış hat için metni çizin
            cv2.putText(frame, line, position, font, font_scale, outline_color, thickness + 4, lineType=cv2.LINE_AA)

            # İç kısım için metni çizin
            cv2.putText(frame, line, position, font, font_scale, text_color, thickness, lineType=cv2.LINE_AA)

            # Yeni yüksekliği güncelle
            y_position += text_height + line_spacing

        return frame

    def calculate_screen_display_time(self):
        """
        Calculate the display time for each text on the screen based on the total frame count.
        """
        total_length = sum(len(string) for string in self.text_array)

        quote_display_count = self.total_frame_count // total_length

        display_reminder_per_quote = (self.total_frame_count % total_length) // len(self.text_array)

        unused_frames = self.total_frame_count - ((quote_display_count * total_length) + (
                display_reminder_per_quote * len(self.text_array)))

        self.text_display_timer_on_screen = {index: (len(string) * quote_display_count) + display_reminder_per_quote
                                             for index, string in enumerate(self.text_array)}

        max_value_key = max(self.text_display_timer_on_screen, key=self.text_display_timer_on_screen.get)

        self.text_display_timer_on_screen[max_value_key] = self.text_display_timer_on_screen[
                                                               max_value_key] + unused_frames

    def display_text_on_screen(self, resized_frame):
        """
        Display text on the resized frame according to the pre-calculated display times.

        Args:
            resized_frame (numpy.ndarray): The resized frame.

        Returns:
            numpy.ndarray: The frame with displayed text.
        """

        if self.display_counter < self.text_display_timer_on_screen[self.display_index]:

            background_with_text = self.add_custom_text_to_center(resized_frame,
                                                                  self.text_array[self.display_index],
                                                                  self.video_properties['width'],
                                                                  self.video_properties['height'],
                                                                  font_scale=2)

            self.display_counter += 1
        else:
            background_with_text = resized_frame
            self.display_counter = 0

            self.display_index = self.display_index + 1 if self.display_index < len(self.text_array) else len(
                self.text_array)

        return background_with_text

    def process_video(self):
        """
        Process the video by adding text to each frame and write the result to an output video file.
        """
        self.out = cv2.VideoWriter(
            self.video_properties['output_path'],
            self.fourcc,
            self.cap.get(cv2.CAP_PROP_FPS),
            (self.video_properties['width'], self.video_properties['height'])
        )

        self.calculate_screen_display_time()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # # Resize the frame
            resized_frame = cv2.resize(frame, (self.video_properties['width'], self.video_properties['height']))
            # Write the resized frame to the output video
            self.out.write(self.display_text_on_screen(resized_frame))

            # text_bg = self.display_text_on_screen(frame)
            # rotate_frame = cv2.rotate(text_bg, cv2.ROTATE_90_CLOCKWISE)
            # self.out.write(rotate_frame)

        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    video = {
        'input_path': '',
        'output_path': '',
        'width': 1080,
        'height': 1920,
    }
    display_text = [
        "Empower your evolution.\nEvery step of improvement\nis a stride toward power."
    ]

    video_processor = VideoProcessor(video_properties=video, text_array=display_text)
    video_processor.process_video()
