package pt.carreira.codigoestrada

import android.content.Context

class ProgressStore(context: Context) {
    private val prefs = context.getSharedPreferences("codigo_estrada_progress", Context.MODE_PRIVATE)

    var answered: Int
        get() = prefs.getInt("answered", 0)
        private set(value) = prefs.edit().putInt("answered", value).apply()

    var correct: Int
        get() = prefs.getInt("correct", 0)
        private set(value) = prefs.edit().putInt("correct", value).apply()

    var examsTaken: Int
        get() = prefs.getInt("exams_taken", 0)
        private set(value) = prefs.edit().putInt("exams_taken", value).apply()

    var examsPassed: Int
        get() = prefs.getInt("exams_passed", 0)
        private set(value) = prefs.edit().putInt("exams_passed", value).apply()

    var bestExamScore: Int
        get() = prefs.getInt("best_exam_score", 0)
        private set(value) = prefs.edit().putInt("best_exam_score", value).apply()

    var latestExamScore: Int
        get() = prefs.getInt("latest_exam_score", -1)
        private set(value) = prefs.edit().putInt("latest_exam_score", value).apply()

    val wrongIds: Set<String>
        get() = prefs.getStringSet("wrong_ids", emptySet())?.toSet() ?: emptySet()

    val favoriteIds: Set<String>
        get() = prefs.getStringSet("favorite_ids", emptySet())?.toSet() ?: emptySet()

    fun attemptsFor(questionId: String): Int = prefs.getInt("attempts_$questionId", 0)
    fun correctFor(questionId: String): Int = prefs.getInt("correct_$questionId", 0)
    fun missesFor(questionId: String): Int = prefs.getInt("misses_$questionId", 0)
    fun streakFor(questionId: String): Int = prefs.getInt("streak_$questionId", 0)

    fun reviewPriority(questionId: String): Int {
        val misses = missesFor(questionId)
        val streak = streakFor(questionId)
        val attempts = attemptsFor(questionId)
        return misses * 10 + attempts - streak * 3
    }

    fun topicAttempts(topic: Topic): Int = prefs.getInt("topic_attempts_${topic.name}", 0)
    fun topicCorrect(topic: Topic): Int = prefs.getInt("topic_correct_${topic.name}", 0)

    fun recordAnswer(question: Question, isCorrect: Boolean) {
        answered += 1
        if (isCorrect) correct += 1

        val id = question.id
        val attempts = attemptsFor(id) + 1
        val qCorrect = correctFor(id) + if (isCorrect) 1 else 0
        val misses = missesFor(id) + if (isCorrect) 0 else 1
        val streak = if (isCorrect) streakFor(id) + 1 else 0
        val tAttempts = topicAttempts(question.topic) + 1
        val tCorrect = topicCorrect(question.topic) + if (isCorrect) 1 else 0

        val nextWrong = wrongIds.toMutableSet()
        if (isCorrect) nextWrong.remove(id) else nextWrong.add(id)

        prefs.edit()
            .putInt("attempts_$id", attempts)
            .putInt("correct_$id", qCorrect)
            .putInt("misses_$id", misses)
            .putInt("streak_$id", streak)
            .putInt("topic_attempts_${question.topic.name}", tAttempts)
            .putInt("topic_correct_${question.topic.name}", tCorrect)
            .putStringSet("wrong_ids", nextWrong)
            .apply()
    }

    fun recordExam(score: Int, total: Int) {
        examsTaken += 1
        latestExamScore = score
        if (score >= 27 && total == 30) examsPassed += 1
        if (score > bestExamScore && total == 30) bestExamScore = score
    }

    fun toggleFavorite(questionId: String): Boolean {
        val next = favoriteIds.toMutableSet()
        val nowFavorite = if (questionId in next) {
            next.remove(questionId)
            false
        } else {
            next.add(questionId)
            true
        }
        prefs.edit().putStringSet("favorite_ids", next).apply()
        return nowFavorite
    }

    fun reset() {
        prefs.edit().clear().apply()
    }
}
