# C4 - report task for the frequency assistant.
# Runs the assistant on the given cryptogram and checks how many letters of the
# suggested mapping are right. The real key below was worked out by hand
# (starting from the report's trigram/bigram hints), assist.py never uses it.
# Run with: py -m experiments.measure_assist
from substitution.breakers.assist import suggested_mapping, report
from utils.basics import normalise
from utils.constants import ENGLISH_FREQUENCY_TABLE

CRYPTOGRAM = """QATNT YSMHQ XJOCY HKATM FSNQI TUTMP TKTIP JIDTT KHIGQ ATCEG
JMHQA FNTYM TQRTY CSNTJ IEXQA TDTXY CIRTY ACIGT PVATI HQHNY
JFKMJ FHNTP"""

# cipher -> plain
TRUE_KEY = {
    'A': 'H', 'C': 'A', 'D': 'K', 'E': 'L', 'F': 'M', 'G': 'G', 'H': 'I',
    'I': 'N', 'J': 'O', 'K': 'P', 'M': 'R', 'N': 'S', 'O': 'F', 'P': 'D',
    'Q': 'T', 'R': 'B', 'S': 'U', 'T': 'E', 'U': 'V', 'V': 'W', 'X': 'Y',
    'Y': 'C',
}
TRUE_PLAINTEXT = (
    "THE SECURITY OF A CIPHER MUST NEVER DEPEND ON KEEPING THE ALGORITHM "
    "SECRET BECAUSE ONLY THE KEY CAN BE CHANGED WHEN IT IS COMPROMISED"
)


if __name__ == "__main__":
    print(report(CRYPTOGRAM, "en"))
    print()

    letters = normalise(CRYPTOGRAM)
    mapping = suggested_mapping(letters, ENGLISH_FREQUENCY_TABLE)
    correct = sum(1 for c, p in mapping.items() if TRUE_KEY.get(c) == p)
    print(f"Suggested mapping accuracy: {correct}/{len(TRUE_KEY)} letters correct")
    print(f"Real plaintext: {TRUE_PLAINTEXT}")
