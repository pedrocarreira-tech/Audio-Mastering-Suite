package pt.carreira.codigoestrada

enum class Screen {
    HOME, STUDY, SIGNS, EXAMPLES, TOPIC_TEST, PRACTICE, EXAM, REVIEW_ERRORS, FAVORITES, STATS, RESULT
}

enum class QuizMode { PRACTICE, TOPIC, EXAM_B, REVIEW_ERRORS, FAVORITES }

enum class Difficulty(val label: String) {
    EASY("Fácil"), MEDIUM("Médio"), HARD("Difícil")
}

enum class Topic(val label: String) {
    SIGNALS("Sinalização"),
    POSITION("Posição e manobras"),
    PRIORITY("Prioridade"),
    ROUNDABOUTS("Rotundas"),
    SPEED("Velocidade"),
    OVERTAKING("Ultrapassagem"),
    PARKING("Paragem e estacionamento"),
    LIGHTS("Luzes"),
    SAFETY("Segurança"),
    ALCOHOL("Álcool e distração"),
    MOTORWAY("Autoestrada"),
    PEDESTRIANS("Peões e velocípedes")
}

enum class SignCategory(val label: String) {
    DANGER("Perigo"),
    YIELD_PRIORITY("Cedência e prioridade"),
    PROHIBITION("Proibição"),
    OBLIGATION("Obrigação"),
    INFORMATION("Informação")
}

enum class SignKind {
    STOP,
    YIELD,
    PRIORITY_ROAD,
    NO_ENTRY,
    SPEED50,
    NO_PARKING,
    NO_STOPPING,
    ROUNDABOUT,
    CYCLE_PATH,
    PEDESTRIAN,
    PARKING,
    MOTORWAY,
    CHILDREN,
    SLIPPERY,
    ROADWORKS,
    PEDESTRIAN_AHEAD,
    CURVE_RIGHT,
    BUMP,
    GRAVEL,
    FALLING_ROCKS,
    WIND,
    LOW_VISIBILITY,
    TUNNEL_AHEAD,
    TRAFFIC_LIGHTS_AHEAD,
    PRIORITY_RIGHT_AHEAD,
    TWO_WAY_TRAFFIC,
    LEVEL_CROSSING,
    END_PRIORITY,
    NARROW_YIELD,
    NARROW_PRIORITY,
    ROUNDABOUT_AHEAD
}

data class RoadSign(
    val kind: SignKind,
    val code: String,
    val category: SignCategory,
    val title: String,
    val meaning: String,
    val tip: String,
    val legalRef: String
)

data class Lesson(
    val topic: Topic,
    val title: String,
    val summary: String,
    val bullets: List<String>,
    val legalRef: String
)

data class Scenario(
    val title: String,
    val body: String,
    val takeaway: String,
    val kind: String,
    val legalRef: String
)

data class Question(
    val id: String,
    val topic: Topic,
    val text: String,
    val options: List<String>,
    val answer: Int,
    val explanation: String,
    val legalRef: String,
    val sign: SignKind? = null,
    val difficulty: Difficulty = Difficulty.MEDIUM
)

data class QuizResult(
    val mode: QuizMode,
    val score: Int,
    val total: Int,
    val elapsedSeconds: Int,
    val wrongIds: List<String>,
    val unanswered: Int = 0,
    val topic: Topic? = null
)
