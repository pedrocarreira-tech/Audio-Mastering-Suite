package pt.carreira.codigoestrada

private val activeSeedIds = setOf(
    "SIG01","SIG02","SIG03","SIG04","SIG05","SIG06","SIG07","SIG08","SIG09","SIG10",
    "POS01","POS02","POS05","PRI01","PRI02","PRI03","PRI04","ROT01","ROT02","ROT03","ROT05",
    "VEL01","VEL02","VEL03","VEL04","VEL05","ULT02","ULT03","ULT04","ULT05","PAR01","PAR02",
    "PAR03","PAR04","PAR05","LUZ01","LUZ03","LUZ04","LUZ05","SEG01","SEG03","SEG04","SEG05",
    "ALC01","ALC02","ALC03","ALC04","ALC05","AUT01","AUT02","AUT03","AUT04","AUT05","PEO03",
    "PEO04","PEO05","SIG11","SIG12","SIG13","SIG14","SIG15","SIG16","SIG17","SIG18","POS06",
    "POS08","PRI06","PRI07","PRI08","ROT06","ROT07","VEL07","VEL08","VEL09","ULT06","ULT09",
    "PAR06","PAR07","PAR08","PAR09","LUZ06","LUZ07","SEG06","SEG07","ALC06","AUT06","AUT07",
    "V4SIG01","V4SIG02","V4SIG03","V4SIG04","V4SIG05","V4SIG06","V4SIG07","V4SIG08","V4SIG09","V4SIG10",
    "V4POS02","V4POS03","V4POS04","V4POS05","V4POS06","V4POS09","V4POS10","V4PRI02","V4PRI03","V4PRI04",
    "V4PRI05","V4PRI06","V4PRI07","V4PRI08","V4PRI10","V4ROT01","V4ROT02","V4ROT03","V4ROT04","V4ROT05",
    "V4ROT07","V4ROT10","V4VEL01","V4VEL02","V4VEL03","V4VEL04","V4VEL05","V4VEL06","V4VEL10","V4ULT02",
    "V4ULT04","V4ULT05","V4ULT06","V4ULT07","V4ULT08","V4ULT09","V4ULT10","V4PAR01","V4PAR02","V4PAR03",
    "V4PAR04","V4PAR05","V4PAR06","V4PAR07","V4PAR08","V4PAR09","V4PAR10","V4LUZ01","V4LUZ02","V4LUZ05",
    "V4LUZ06","V4LUZ07","V4LUZ08","V4LUZ09","V4SEG01","V4SEG02","V4SEG03","V4SEG05","V4SEG06","V4SEG08",
    "V4SEG09","V4SEG10","V4ALC01","V4ALC02","V4ALC03","V4ALC04","V4ALC05","V4ALC06","V4ALC07","V4ALC08",
    "V4ALC09","V4ALC10","V4AUT01","V4AUT02","V4AUT03","V4AUT05","V4AUT07","V4AUT08","V4AUT09","V4AUT10",
    "V4PEA01","V4PEA02","V4PEA05","V4PEA06","V4PEA07","V4PEA10"
)

private fun lowerInitialV6(text: String): String = text.replaceFirstChar { it.lowercase() }

private fun expandQuestionV6(seed: Question): List<Question> {
    val lower = lowerInitialV6(seed.text)
    return listOf(
        seed.copy(id = "${seed.id}-A"),
        seed.copy(id = "${seed.id}-B", text = "Considerando apenas os dados apresentados, $lower"),
        seed.copy(id = "${seed.id}-C", text = "Numa situação prática de condução, $lower"),
        seed.copy(id = "${seed.id}-D", text = "De acordo com a regra aplicável, $lower"),
        seed.copy(id = "${seed.id}-E", text = "Sem pressupor qualquer exceção não indicada, $lower")
    )
}

val activeQuestionSeeds: List<Question> = (baseQuestions + v4Questions).filter { it.id in activeSeedIds }
val expandedQuestionsV6: List<Question> = activeQuestionSeeds.flatMap(::expandQuestionV6)

private fun lessonChunk(base: Lesson, titlePrefix: String, bulletRange: IntRange): Lesson {
    val selected = bulletRange.mapNotNull { base.bullets.getOrNull(it) }
    return Lesson(
        topic = base.topic,
        title = "$titlePrefix — ${base.title}",
        summary = base.summary,
        bullets = if (selected.isNotEmpty()) selected else base.bullets,
        legalRef = base.legalRef
    )
}

val expandedLessonsV6: List<Lesson> = baseLessons.flatMap { base ->
    listOf(
        base,
        lessonChunk(base, "Fundamentos", 0..1),
        lessonChunk(base, "Aplicação prática", 2..3),
        Lesson(
            topic = base.topic,
            title = "Revisão e erros frequentes — ${base.title}",
            summary = "Revisão dirigida: distingue a regra-base das exceções e aplica-a ao contexto descrito.",
            bullets = base.bullets.takeLast(3),
            legalRef = base.legalRef
        )
    )
}
