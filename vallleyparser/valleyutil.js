/**
 * Created by yangling on 2017/8/19.
 */

function p(question, oldStr, newStr, conceptsStr, lineNum) {
    // document.write('Process Finished')
    // document.write(oldStr)


    $("#old_question").html("")

    if ($("#line_number").html() != lineNum+""){
        $(".vField").val("")
        $("#concept_result").html("")
    }

    console.warn(conceptsStr)



    $.each(oldStr.split(" "), function(index, value){
        $("#old_question").append("<a href='' class='dword' onclick='return false;'>" + value + "</a> ");
    })

    // $("#old_question").html(oldStr)

    $("#question").html(question)

    $("#new_question").html(newStr)

    $("#concept_words").val(conceptsStr)

    console.warn("行号: "+lineNum)

    $("#line_number").html(lineNum)
}


$(document).on("click contextmenu", "a.dword",  function(e) {
    switch (e.which) {
        case 1:
            appendDict(event.target)
            break;
        default:
            appendConcept(event.target)
    }

    e.preventDefault();
});

var appendDict = function (t) {
    s = $("#jieba_words").val() + " "+ $(t).html()
    $("#jieba_words").val(s)
}

var appendConcept = function (t) {
    s = $("#concept_words").val() + " "+ $(t).html();
    $("#concept_words").val(s)
}

var saveDict = function(){
    str = $("#jieba_words").val();
    console.warn("保存字典: "+str)
    window.valleyDict.save(str);
}

var removeGarbage = function(){
    str = $("#jieba_words").val();
    console.warn("保存垃圾词汇: "+str)
    window.valleyDict.saveGarbageWords(str);
}

//保存停用词
var stopDict = function(){
    str = $("#jieba_words").val();
    console.warn("保存停用词: "+str)
    window.valleyDict.stop(str);
}

var saveConcepts = function(){
    str = $("#concept_words").val();
    console.warn("保存  concepts: " + str)
    window.concepts.save(str);
}

var searchConcept = function () {
    str = $("#search_concept").val()
    window.concepts.search(str)
}

var conceptSearched = function (str) {
    $("#concept_result").html(str)
}


new QWebChannel(qt.webChannelTransport, function (channel) {
    console.warn('qwebchannel triggered');
    window.valleys = channel.objects.valleys;
    window.valleyDict = channel.objects.valleyDict;
    window.concepts = channel.objects.concepts;

    window.valleys.valleyRecieved.connect(p);
    window.concepts.conceptSearched.connect(conceptSearched)

    window.valleys.reload();
    // print(window.lineReader.value)
});

var next = function(){
    window.valleys.next(1)
}
var nextPage = function(){
    window.valleys.next(10)
}
var nextEnd = function(){
    window.valleys.next(-1)
}
var prev = function(){
    window.valleys.prev(1)
}
var prevPage = function(){
    window.valleys.prev(10)
}
var prevEnd = function(){
    window.valleys.prev(-1)
}