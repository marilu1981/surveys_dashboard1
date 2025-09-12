from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static
from textual.containers import Vertical
import pyjokes
import duckdb
    
class QueryApp(App):
    CSS_PATH = None
    BINDINGS = [("q", "quit", "Quit")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            self.query_display = Static("Click the button to run query!")
            yield self.query_display
            yield Button("Run Query", id="query-button")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "query-button":
            query = """
            SELECT 
                question_text,
                response_text_x,
                COUNT(*) AS answer_count
            FROM 'final_data_12Sept2025_processed.csv'
            WHERE date BETWEEN '2025-01-01' AND '2025-09-07'
            GROUP BY question_text, response_text_x
            """
            result = duckdb.query(query).to_df()
            self.query_display.update(str(result))
        

if __name__ == "__main__":
    import sys
    try:
        import pyjokes
    except ImportError:
        print("Installing pyjokes...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyjokes"])
    QueryApp().run()