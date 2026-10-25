import chess
import chess.engine
import time

# Chemin vers l'exécutable Stockfish sur votre système
STOCKFISH_PATH = "stockfish" 

class ChessArbiter:
    """L'Arbitre officiel qui veille au respect des règles et analyse le plateau."""
    def __init__(self, board):
        self.board = board

    def validate_and_apply_move(self, move_uci, is_robot=False):
        """Vérifie la légalité d'un coup selon les règles officielles des échecs."""
        try:
            move = chess.Move.from_uci(move_uci)
            if move not in self.board.legal_moves:
                actor = "Le robot" if is_robot else "Vous"
                print(f"❌ [Arbitre] Coup illégal détecté pour {actor} : {move_uci}. Ce coup enfreint les règles.")
                return False
            
            # Applique le coup si tout est correct
            self.board.push(move)
            return True
        except ValueError:
            print(f"❌ [Arbitre] Format de coup invalide : '{move_uci}'. Utilisez le format UCI (ex: e2e4).")
            return False

    def analyze_board_state(self):
        """Analyse l'état de la partie après un coup et rend un verdict."""
        if self.board.is_checkmate():
            winner = "les Noirs" if self.board.turn == chess.WHITE else "les Blancs"
            return f"🏁 [Arbitre] ÉCHEC ET MAT ! La partie est terminée. Victoire de {winner} !"
        
        elif self.board.is_stalemate():
            return "🤝 [Arbitre] PAT ! C'est une égalité (match nul)."
        
        elif self.board.is_insufficient_material():
            return "🤝 [Arbitre] Égalité par matériel insuffisant !"
        
        elif self.board.is_check():
            king_color = "des Blancs" if self.board.turn == chess.WHITE else "des Noirs"
            return f"⚠️ [Arbitre] ALerte : Le Roi {king_color} est en ÉCHEC !"
        
        return None


class ChessRobotAI:
    def __init__(self, difficulty="easy"):
        self.board = chess.Board()
        self.difficulty = difficulty
        self.arbiter = ChessArbiter(self.board)
        
        try:
            self.engine = chess.engine.SimpleEngine.spawn_uci(STOCKFISH_PATH)
        except Exception as e:
            print(f"Erreur : Impossible de lancer Stockfish. Vérifiez le chemin. ({e})")
            exit(1)
            
        self.configure_difficulty()

    def configure_difficulty(self):
        """Configure les paramètres de Stockfish selon le mode choisi."""
        if self.difficulty == "easy":
            self.engine.configure({"Skill Level": 3})
            self.limit = chess.engine.Limit(time=0.2)
            print("🤖 Mode Facile activé (Niveau 3 - Idéal pour débuter).")
            
        elif self.difficulty == "intermediate":
            self.engine.configure({"Skill Level": 12})
            self.limit = chess.engine.Limit(time=0.5)
            print("🤖 Mode Intermédiaire activé (Niveau 12 - Erreurs tactiques possibles).")
        
        elif self.difficulty == "hard":
            self.engine.configure({"Skill Level": 20})
            self.limit = chess.engine.Limit(time=2.0)
            print("🤖 Mode Difficile activé (Niveau MAX - Ne pardonne rien).")
        else:
            raise ValueError("Mode inconnu. Choisissez 'easy', 'intermediate' ou 'hard'.")

    def describe_move(self, move):
        """Traduit un coup en une phrase claire en français."""
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
            target_name = piece_names.get(target_piece.piece_type, "pièce") if target_piece else "pion"
            return f"Le {piece_name} capture le {target_name} adverse de {from_sq} vers {to_sq}"
        else:
            return f"Le {piece_name} se déplace de {from_sq} vers {to_sq}"

    def play_robot_turn(self):
        """Calcule et joue le coup du robot sous le contrôle de l'arbitre."""
        if self.board.is_game_over():
            return None
        
        print("Le robot réfléchit...")
        result = self.engine.play(self.board, self.limit)
        move = result.move
        
        # Description textuelle avant de jouer
        move_description = self.describe_move(move)
        
        # L'arbitre valide et applique le coup du robot
        self.arbiter.validate_and_apply_move(move.uci(), is_robot=True)
        return move_description

    def close(self):
        """Ferme proprement le moteur Stockfish."""
        self.engine.quit()


# --- Boucle principale du jeu ---
if __name__ == "__main__":
    print("=== BIENVENUE DANS LE ROBOT D'ÉCHECS (AVEC ARBITRE) ===")
    print("Choisissez le mode de difficulté :")
    print("1. Facile")
    print("2. Intermédiaire")
    print("3. Difficile")
    
    choice = input("Votre choix (1, 2 ou 3) : ").strip()
    if choice == "1":
        diff_mode = "easy"
    elif choice == "3":
        diff_mode = "hard"
    else:
        diff_mode = "intermediate"
        
    robot = ChessRobotAI(difficulty=diff_mode)
    
    print("\nL'échiquier est prêt. Les Blancs sont aux échecs.")
    print("Entrez vos coups au format UCI (ex: 'e2e4'). Tapez 'exit' pour quitter.\n")

    try:
        while not robot.board.is_game_over():
            print("\n" + str(robot.board))
            print("-" * 30)
            
            # Tour du joueur humain
            human_move = input("Votre coup : ")
            if human_move.lower() == 'exit':
                break
                
            # L'arbitre valide votre coup
            if not robot.arbiter.validate_and_apply_move(human_move, is_robot=False):
                continue
                
            # Analyse de l'arbitre après votre coup
            verdict = robot.arbiter.analyze_board_state()
            if verdict:
                print(verdict)
                if robot.board.is_game_over():
                    break
                
            # Tour du robot
            robot_action_text = robot.play_robot_turn()
            if robot_action_text:
                print(f"🤖 Annonce du robot : {robot_action_text}")
                
            # Analyse de l'arbitre après le coup du robot
            verdict = robot.arbiter.analyze_board_state()
            if verdict:
                print(verdict)
                if robot.board.is_game_over():
                    break

        print("\nPartie terminée !")
        print("Résultat officiel :", robot.board.result())

    finally:
        robot.close()
