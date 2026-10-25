import chess
import chess.engine
import time

STOCKFISH_PATH = "stockfish" 

class ChessRobotAI:
    def __init__(self, difficulty="easy", player_color=chess.WHITE):
        self.board = chess.Board()
        self.difficulty = difficulty
        self.player_color = player_color
        
        try:
            self.engine = chess.engine.SimpleEngine.spawn_uci(STOCKFISH_PATH)
        except Exception as e:
            print(f"Erreur : Impossible de lancer Stockfish. Vérifiez le chemin. ({e})")
            exit(1)
            
        self.configure_difficulty()

    def configure_difficulty(self):
        if self.difficulty == "easy":
            # Mode Facile (Niveau modéré d'erreurs)
            self.engine.configure({"Skill Level": 3})
            self.limit = chess.engine.Limit(time=0.2)
            print("🤖 [biche_chess] Mode Facile activé.")
        elif self.difficulty == "intermediate":
            # Mode Intermédiaire
            self.engine.configure({"Skill Level": 10})
            self.limit = chess.engine.Limit(time=0.5)
            print("🤖 [biche_chess] Mode Intermédiaire activé.")
        elif self.difficulty == "hard":
            # Mode Difficile (Niveau Max)
            self.engine.configure({"Skill Level": 20})
            self.limit = chess.engine.Limit(time=2.0)
            print("🤖 [biche_chess] Mode Difficile activé.")
        else:
            raise ValueError("Mode inconnu.")

    def format_move_description(self, move, actor_prefix):
        """Formate le texte sous la forme : [Acteur] : [Pièce] [départ] en [arrivée]"""
        piece = self.board.piece_at(move.from_square)
        if not piece:
            return str(move)
        
        piece_names = {
            chess.PAWN: "Pion",
            chess.KNIGHT: "Cavalier",
            chess.BISHOP: "Fou",
            chess.ROOK: "Tour",
            chess.QUEEN: "Dame",
            chess.KING: "Roi"
        }
        
        piece_name = piece_names.get(piece.piece_type, "Pièce")
        from_sq = chess.SQUARE_NAMES[move.from_square]
        to_sq = chess.SQUARE_NAMES[move.to_square]
        
        target_piece = self.board.piece_at(move.to_square)
        if target_piece or self.board.is_en_passant(move):
            target_name = piece_names.get(target_piece.piece_type, "pion") if target_piece else "pion"
            return f"{actor_prefix} : {piece_name} {from_sq} en {to_sq} (capture le {target_name})"
        else:
            return f"{actor_prefix} : {piece_name} {from_sq} en {to_sq}"

    def play_robot_turn(self):
        if self.board.is_game_over():
            return None
        
        print("biche_chess réfléchit...")
        result = self.engine.play(self.board, self.limit)
        move = result.move
        
        description = self.format_move_description(move, "🤖 biche_chess")
        self.board.push(move)
        return description

    def play_human_turn(self, move_uci):
        try:
            # Convertit la saisie en minuscules pour accepter les majuscules (ex: E2E4)
            move_uci_cleaned = move_uci.strip().lower()
            move = chess.Move.from_uci(move_uci_cleaned)
            
            if move in self.board.legal_moves:
                description = self.format_move_description(move, "👤 Vous")
                self.board.push(move)
                print(description)
                return True
            else:
                print("Coup illégal ! Réessayez.")
                return False
        except ValueError:
            print("Format de coup invalide (utilisez ex: e2e4 ou E2E4).")
            return False

    def close(self):
        self.engine.quit()

if __name__ == "__main__":
    print("=== ♟️ biche_chess - CONFIGURATION DU CERVEAU PYTHON ♔ ===")
    
    print("Choisissez le niveau de difficulté :")
    print("1. Facile")
    print("2. Intermédiaire")
    print("3. Difficile")
    
    diff_choice = input("Votre choix (1 à 3) : ").strip()
    
    mapping = {
        "1": "easy",
        "2": "intermediate",
        "3": "hard"
    }
    diff_mode = mapping.get(diff_choice, "easy")
    
    print("\nChoisissez votre couleur :")
    print("1. Blancs (Vous commencez)")
    print("2. Noirs (Le robot commence)")
    color_choice = input("Votre choix (1 ou 2) : ").strip()
    player_color = chess.BLACK if color_choice == "2" else chess.WHITE
    
    robot = ChessRobotAI(difficulty=diff_mode, player_color=player_color)
    
    color_str = "Noirs" if player_color == chess.BLACK else "Blancs"
    print(f"\nPartie lancée sous biche_chess ! Vous jouez les {color_str}. Entrez vos coups au format UCI (ex: 'e2e4' ou 'E2E4'). Tapez 'exit' pour quitter.\n")

    try:
        while not robot.board.is_game_over():
            if robot.board.turn != robot.player_color:
                robot_action_text = robot.play_robot_turn()
                if robot_action_text:
                    print(f"\n{robot_action_text}")
                if robot.board.is_game_over():
                    break

            print("\n" + str(robot.board))
            print("-" * 30)
            
            human_move = input("Votre coup : ")
            if human_move.lower() == 'exit':
                break
                
            if not robot.play_human_turn(human_move):
                continue

        print("\nPartie terminée !")
        print("Résultat :", robot.board.result())

    finally:
        robot.close()
