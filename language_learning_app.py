import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
import requests

class LanguageLearningLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.quote_label = Label(text="Loading Quote...", font_size = 40)
        self.add_widget(self.quote_label)

        self.translation_input = TextInput(hint_text = "Type your translation here", multiline=False)
        self.add_widget(self.translation_input)

        self.language_spinner = Spinner(
            text = "Select Language",
            values = ('es', 'fr', 'de', 'it'), # Example languages: Spanish, French, German, Italian
        )
        self.add_widget(self.language_spinner)

        self.translate_button = Button(text = "Translate", on_press = self.translate_quote)
        self.add_widget(self.translate_button)

        self.refresh_button = Button(text = "Refresh Quote", on_press = self.get_random_quote)
        self.add_widget(self.refresh_button)

        self.translated_label = Label(text="", font_size=40)
        self.add_widget(self.translated_label)

        self.get_random_quote()

    def get_random_quote(self, *args):
            self.translation_input.text = ''
            response = requests.get('https://api.quotable.io/random')
            if response.status_code == 200:
                self.quote = response.json()['content']
                self.quote_label.text = self.quote
            else:
                self.quote_label.text = "Failed to load quote"
    
    def translate_quote(self, *args):
         target_language = self.language_spinner.text
         user_translate = self.translation_input.text
         response = requests.get(
              'https://api.mymemory.translated.net/get',
              params={'q': self.quote, 'langpair': f'en|{target_language}'}
         )

         if response.status_code == 200:
              translated_text = response.json()['responseData']['translatedText']
              self.translated_label.text = f'Correct translation: {translated_text}\nYour Translation: {user_translate}'
         else:
              self.translated_label.text = 'Translation Failed'


class LanguageLearningApp(App):
     def build(self):
          return LanguageLearningLayout()


if __name__ == '__main__':
     LanguageLearningApp().run()



