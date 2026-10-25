import chess
import chess.engine
import time

STOCKFISH_PATH = "stockfish" 

class ChessRobotAI:
    def __init__(self, difficulty="easy"):
        self.board = chess.Board()
        self.difficulty = difficulty
        
        try:
            self.engine = chess.engine.SimpleEngine.spawn_uci(STOCKFISH_PATH)
        except Exception as e:
            print(f"Erreur : Impossible de lancer Stockfish. Vérifiez le chemin. ({e})")
            exit(1)
            
        self.configure_difficulty()

    def configure_difficulty(self):
        if self.difficulty == "easy":
            self.engine.configure({"Skill Level": 3})
            self.limit = chess.engine.Limit(time=0.2)
            print("🤖 Mode Facile activé (Niveau 3).")
        elif self.difficulty == "intermediate":
            self.engine.configure({"Skill Level": 12})
            self.limit = chess.engine.Limit(time=0.5)
            print("🤖 Mode Intermédiaire activé (Niveau 12).")
        elif self.difficulty == "hard":
            self.engine.configure({"Skill Level": 20})
            self.limit = chess.engine.Limit(time=2.0)
            print("🤖 Mode Difficile activé (Niveau MAX).")
        else:
            raise ValueError("Mode inconnu.")

    def format_move_description(self, move, actor_prefix):
        """Formate le texte sous la forme : [Pièce] [départ] en [arrivée]"""
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
        
        # Description avant de pousser sur le plateau
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
    print("=== ROBOT D'ÉCHECS ===")
    print("1. Facile\n2. Intermédiaire\n3. Difficile")
    choice = input("Votre choix (1, 2 ou 3) : ").strip()
    
    diff_mode = "easy" if choice == "1" else ("hard" if choice == "3" else "intermediate")
    robot = ChessRobotAI(difficulty=diff_mode)
    
    print("\nL'échiquier est prêt. Entrez vos coups au format UCI (ex: 'e2e4'). Tapez 'exit' pour quitter.\n")

    try:
        while not robot.board.is_game_over():
            print("\n" + str(robot.board))
            print("-" * 30)
            
            human_move = input("Votre coup : ")
            if human_move.lower() == 'exit':
                break
                
            if not robot.play_human_turn(human_move):
                continue
                
            if robot.board.is_game_over():
                break
                
            robot_action_text = robot.play_robot_turn()
            if robot_action_text:
                print(f"\n{robot_action_text}")

        print("\nPartie terminée !")
        print("Résultat :", robot.board.result())

    finally:
        robot.close()
