"""터미널에서 동작하는 사지선다 퀴즈 게임."""

import json
import os
import random

LINE = "=" * 40
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


class Quiz:
    """문제 하나를 표현한다. 정답은 선택지 번호(1-4)로 관리한다."""

    def __init__(self, question, choices, answer, hint):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def show(self, number):
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def is_correct(self, picked):
        return picked == self.answer

    def answer_text(self):
        return self.choices[self.answer - 1]

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @staticmethod
    def from_dict(data):
        return Quiz(data["question"], data["choices"], data["answer"], data["hint"])


def default_quizzes():
    """저장된 데이터가 없을 때 사용하는 기본 문제. 주제는 컴퓨터 구조와 운영체제."""
    return [
        Quiz(
            "CPU가 명령어 하나를 처리하는 기본 사이클의 순서는?",
            ["해석 - 인출 - 실행", "인출 - 해석 - 실행", "실행 - 인출 - 해석", "인출 - 실행 - 해석"],
            2,
            "명령어를 먼저 가져와야 무엇을 할지 정할 수 있습니다.",
        ),
        Quiz(
            "프로그램 카운터(PC)가 담고 있는 값은?",
            [
                "직전에 실행한 명령어의 주소",
                "연산에 사용할 피연산자",
                "다음에 실행할 명령어의 주소",
                "스택의 최상단 주소",
            ],
            3,
            "이름 그대로 다음 차례를 가리킵니다.",
        ),
        Quiz(
            "CPU와 주기억장치 사이에 캐시 메모리를 두는 이유는?",
            [
                "보조기억장치의 용량을 늘리기 위해",
                "두 장치의 속도 차이를 줄이기 위해",
                "전력 소비를 줄이기 위해",
                "프로세스 간에 데이터를 공유하기 위해",
            ],
            2,
            "CPU는 빠르고 주기억장치는 느립니다.",
        ),
        Quiz(
            "같은 프로세스에 속한 스레드들이 공유하지 않는 영역은?",
            ["코드 영역", "데이터 영역", "힙 영역", "스택 영역"],
            4,
            "함수 호출 정보는 스레드마다 따로 있어야 합니다.",
        ),
        Quiz(
            "교착 상태가 발생하기 위한 네 가지 필요조건에 해당하지 않는 것은?",
            ["상호 배제", "점유와 대기", "선점", "순환 대기"],
            3,
            "나머지 셋과 달리 하나는 '뺏을 수 없다'는 조건입니다.",
        ),
        Quiz(
            "페이지 폴트가 발생했을 때 필요한 페이지를 메모리로 올리는 주체는?",
            ["운영체제", "컴파일러", "캐시 컨트롤러", "링커"],
            1,
            "메모리 관리를 맡는 소프트웨어입니다.",
        ),
        Quiz(
            "프레임 수를 늘렸는데 오히려 페이지 폴트가 늘어나는 현상이 나타나는 교체 알고리즘은?",
            ["FIFO", "LRU", "LFU", "OPT"],
            1,
            "벨라디의 이상 현상이라고 부릅니다.",
        ),
        Quiz(
            "문맥 교환이 일어날 때 프로세스의 실행 상태를 저장해 두는 자료구조는?",
            ["TLB", "MMU", "PCB", "ALU"],
            3,
            "프로세스마다 하나씩 두는 제어 블록입니다.",
        ),
    ]


def read_text(prompt):
    """빈 문자열이 아닌 입력을 받을 때까지 다시 묻는다."""
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        print("입력이 비어 있습니다. 다시 입력하세요.")


def read_int(prompt, low, high, extra=()):
    """low 이상 high 이하의 정수를 받을 때까지 다시 묻는다. extra 의 글자는 그대로 돌려준다."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() in extra:
            return raw.lower()
        if not raw:
            print(f"입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print(f"잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        if not low <= value <= high:
            print(f"잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        return value


class QuizGame:
    """퀴즈 목록과 최고 점수를 들고 메뉴 전체를 진행한다."""

    def __init__(self):
        self.quizzes = []
        self.best_score = None

    def load(self):
        """state.json 에서 퀴즈와 최고 점수를 읽는다. 파일이 없으면 기본 퀴즈를 사용한다."""
        if not os.path.exists(STATE_FILE):
            self.quizzes = default_quizzes()
            self.best_score = None
            return
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            self.best_score = data["best_score"]
        except (OSError, ValueError, TypeError, KeyError):
            print(f"{os.path.basename(STATE_FILE)} 을 읽을 수 없어 기본 퀴즈로 시작합니다.")
            self.quizzes = default_quizzes()
            self.best_score = None
            return
        record = "기록 없음" if self.best_score is None else f"{self.best_score}점"
        print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고 점수 {record})")

    def save(self):
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"저장에 실패했습니다. ({error})")

    def show_menu(self):
        print()
        print(LINE)
        print("           나만의 퀴즈 게임")
        print(LINE)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 종료")
        print(LINE)

    def play(self):
        """고른 개수만큼 무작위로 출제하고 최고 점수를 갱신한다."""
        if not self.quizzes:
            print()
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return

        print()
        total = read_int(f"몇 문제를 풀까요? (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        selected = random.sample(self.quizzes, total)

        print()
        print(f"퀴즈를 시작합니다. (총 {total}문제)")
        correct = 0
        hinted = 0
        earned = 0.0
        for number, quiz in enumerate(selected, start=1):
            print()
            print("-" * 40)
            quiz.show(number)
            print()
            used_hint = False
            picked = read_int("정답 입력 (h: 힌트): ", 1, 4, extra=("h",))
            while picked == "h":
                print(f"힌트: {quiz.hint}")
                used_hint = True
                picked = read_int("정답 입력 (h: 힌트): ", 1, 4, extra=("h",))
            if used_hint:
                hinted += 1
            if quiz.is_correct(picked):
                print("정답입니다.")
                correct += 1
                earned += 0.5 if used_hint else 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번 {quiz.answer_text()} 입니다.")

        score = round(earned / total * 100)
        print()
        print(LINE)
        print(f"결과: {total}문제 중 {correct}문제 정답 ({score}점)")
        if hinted:
            print(f"힌트를 본 {hinted}문제는 절반만 인정했습니다.")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("새로운 최고 점수입니다.")
        print(LINE)
        self.save()

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호, 힌트를 입력받아 목록에 추가한다."""
        print()
        print("새로운 퀴즈를 추가합니다.")
        print()
        question = read_text("문제를 입력하세요: ")
        choices = [read_text(f"선택지 {i}: ") for i in range(1, 5)]
        answer = read_int("정답 번호 (1-4): ", 1, 4)
        hint = read_text("힌트: ")
        self.quizzes.append(Quiz(question, choices, answer, hint))
        print()
        print("퀴즈가 추가되었습니다.")
        self.save()

    def list_quizzes(self):
        print()
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print("-" * 40)

    def delete_quiz(self):
        """번호로 퀴즈 하나를 골라 목록에서 지운다."""
        if not self.quizzes:
            print()
            print("등록된 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        print()
        number = read_int(f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        removed = self.quizzes.pop(number - 1)
        print()
        print(f"삭제했습니다: {removed.question}")
        self.save()

    def show_score(self):
        print()
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어보세요.")
            return
        print(f"최고 점수: {self.best_score}점")

    def run(self):
        while True:
            self.show_menu()
            choice = read_int("선택: ", 1, 6)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.delete_quiz()
            else:
                print("게임을 종료합니다.")
                break


def main():
    game = QuizGame()
    game.load()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print()
        print("입력이 중단되어 게임을 종료합니다.")
        game.save()


if __name__ == "__main__":
    main()
