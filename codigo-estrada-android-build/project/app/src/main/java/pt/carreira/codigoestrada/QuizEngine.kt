package pt.carreira.codigoestrada

import kotlin.random.Random

object QuizEngine {
    /**
     * Builds a 30-question Category B simulator set while ensuring broad coverage
     * of all topics represented in the local educational bank.
     *
     * This is a pedagogical balancing strategy; it is not a claim about the exact
     * topic distribution used by IMT in any specific official test.
     */
    fun buildExam(pool: List<Question>, random: Random = Random.Default): List<Question> {
        if (pool.size <= 30) return pool.shuffled(random)

        val selected = mutableListOf<Question>()
        Topic.entries.forEach { topic ->
            selected += pool.filter { it.topic == topic }.shuffled(random).take(2)
        }

        val ids = selected.mapTo(mutableSetOf()) { it.id }
        val remaining = pool.filter { it.id !in ids }.shuffled(random)
        selected += remaining.take((30 - selected.size).coerceAtLeast(0))
        return selected.shuffled(random).take(30)
    }

    fun buildPractice(pool: List<Question>, size: Int = 10, random: Random = Random.Default): List<Question> =
        pool.shuffled(random).take(size)

    fun buildTopicTest(
        pool: List<Question>,
        topic: Topic,
        difficulty: Difficulty? = null,
        size: Int = 10,
        random: Random = Random.Default
    ): List<Question> = pool
        .filter { it.topic == topic }
        .filter { difficulty == null || it.difficulty == difficulty }
        .shuffled(random)
        .take(size)
}
