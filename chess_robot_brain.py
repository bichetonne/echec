import chess
import chess.engine
import time

STOCKFISH_PATH = "stockfish" 

class ChessRobotAI:
    def __init__(self, skill_level=5, player_color=chess.WHITE):
        self.board = chess.Board()
        self.skill_level = max(1, min(20, skill_level)) # Entre 1 et 20
        self.player_color = player_color
        
        try:
            self.engine = chess.engine.SimpleEngine.spawn_uci(STOCKFISH_PATH)
        except Exception as e:
            print(f"Erreur : Impossible de lancer Stockfish. Vérifiez le chemin. ({e})")
            exit(1)
            
        self.configure_difficulty()

    def configure_difficulty(self):
        # Mappe le niveau utilisateur (1-20) sur le Skill Level de Stockfish (0 à 20)
        sf_skill = int((self.skill_level - 1) * 20 / 19)
        self.engine.configure({"Skill Level": sf_skill})
        time_limit = 0.1 + (self.skill_level * 0.08)
        self.limit = chess.engine.Limit(time=time_limit)
        
        # Correspondance textuelle Elo Chess.com pour l'affichage console
        elo_map = {
            1: "250 Elo", 2: "400 Elo", 3: "600 Elo", 4: "800 Elo", 5: "1000 Elo",
            6: "1200 Elo", 7: "1400 Elo", 8: "1550 Elo", 9: "1700 Elo", 10: "1850 Elo",
            11: "2000 Elo", 12: "2150 Elo", 13: "2300 Elo", 14: "2450 Elo", 15: "2600 Elo",
            16: "2750 Elo", 17: "2850 Elo", 18: "2950 Elo", 19: "3050 Elo", 20: "3200 Elo (Max)"
        }
        print(f"🤖 [biche_chess] Niveau {self.skill_level} ({elo_map.get(self.skill_level, '')}) activé.")

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
        
        print("biche_chess réfléchit...")
        result = self.engine.play(self.board, self.limit)
        move = result.move
        
        description = self.format_move_description(move, "🤖 biche_chess")
        self.board.push(move)
        return description

    def play_human_turn(self, move_uci):
        try:
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
    
    try:
        level_input = input("Choisissez le niveau de difficulté (1 à 20) [défaut: 5] : ").strip()
        skill_level = int(level_input) if level_input else 5
    except ValueError:
        skill_level = 5
    
    print("\nChoisissez votre couleur :")
    print("1. Blancs (Vous commencez)")
    print("2. Noirs (Le robot commence)")
    color_choice = input("Votre choix (1 ou 2) : ").strip()
    player_color = chess.BLACK if color_choice == "2" else chess.WHITE
    
    robot = ChessRobotAI(skill_level=skill_level, player_color=player_color)
    
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
