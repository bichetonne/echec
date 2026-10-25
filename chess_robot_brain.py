import chess
import chess.engine
import time

STOCKFISH_PATH = "stockfish" 

class ChessRobotAI:
    def __init__(self, difficulty="sub_200", player_color=chess.WHITE):
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
        if self.difficulty == "sub_200":
            # Niveau ~0-200 Elo (Skill Level 0, le plus faible possible)
            self.engine.configure({"Skill Level": 0})
            self.limit = chess.engine.Limit(time=0.1)
            print("🤖 Mode Débutant activé (0-200 Elo).")
        elif self.difficulty == "sub_600":
            # Niveau ~400-600 Elo (Skill Level 1)
            self.engine.configure({"Skill Level": 1})
            self.limit = chess.engine.Limit(time=0.15)
            print("🤖 Mode Écolier activé (400-600 Elo).")
        elif self.difficulty == "easy":
            # Niveau ~600-800 Elo
            self.engine.configure({"Skill Level": 2})
            self.limit = chess.engine.Limit(time=0.2)
            print("🤖 Mode Facile activé (~600-800 Elo).")
        elif self.difficulty == "easy_plus":
            # Niveau ~1000-1200 Elo
            self.engine.configure({"Skill Level": 7})
            self.limit = chess.engine.Limit(time=0.3)
            print("🤖 Mode Facile + activé (~1000-1200 Elo).")
        elif self.difficulty == "intermediate":
            # Niveau ~1400-1600 Elo
            self.engine.configure({"Skill Level": 14})
            self.limit = chess.engine.Limit(time=0.5)
            print("🤖 Mode Intermédiaire activé (~1400-1600 Elo).")
        elif self.difficulty == "hard":
            # Niveau Maximum (3000+ Elo)
            self.engine.configure({"Skill Level": 20})
            self.limit = chess.engine.Limit(time=2.0)
            print("🤖 Mode Difficile activé (Niveau MAX).")
        else:
            raise ValueError("Mode inconnu.")

    def format_move_description(self, move, actor_prefix):
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
        
        print("Le robot réfléchit...")
        result = self.engine.play(self.board, self.limit)
        move = result.move
        
        description = self.format_move_description(move, "🤖 Robot")
        self.board.push(move)
        return description

    def play_human_turn(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                description = self.format_move_description(move, "👤 Vous")
                self.board.push(move)
                print(description)
                return True
            else:
                print("Coup illégal ! Réessayez.")
                return False
        except ValueError:
            print("Format de coup invalide (utilisez ex: e2e4).")
            return False

    def close(self):
        self.engine.quit()

if __name__ == "__main__":
    print("=== CONFIGURATION DU ROBOT D'ÉCHECS ===")
    
    print("Choisissez le niveau de difficulté :")
    print("1. Débutant (0-200 Elo)")
    print("2. Écolier (400-600 Elo)")
    print("3. Facile (~600-800 Elo)")
    print("4. Facile + (~1000-1200 Elo)")
    print("5. Intermédiaire (~1400-1600 Elo)")
    print("6. Difficile (Niveau Max)")
    
    diff_choice = input("Votre choix (1 à 6) : ").strip()
    
    if diff_choice == "1":
        diff_mode = "sub_200"
    elif diff_choice == "2":
        diff_mode = "sub_600"
    elif diff_choice == "3":
        diff_mode = "easy"
    elif diff_choice == "4":
        diff_mode = "easy_plus"
    elif diff_choice == "5":
        diff_mode = "intermediate"
    elif diff_choice == "6":
        diff_mode = "hard"
    else:
        diff_mode = "sub_200"
    
    print("\nChoisissez votre couleur :")
    print("1. Blancs (Vous commencez)")
    print("2. Noirs (Le robot commence)")
    color_choice = input("Votre choix (1 ou 2) : ").strip()
    player_color = chess.BLACK if color_choice == "2" else chess.WHITE
    
    robot = ChessRobotAI(difficulty=diff_mode, player_color=player_color)
    
    color_str = "Noirs" if player_color == chess.BLACK else "Blancs"
    print(f"\nPartie lancée ! Vous jouez les {color_str}. Entrez vos coups au format UCI (ex: 'e2e4'). Tapez 'exit' pour quitter.\n")

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
