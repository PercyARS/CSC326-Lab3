%include ('Templates/header.tpl')
%include ('Templates/css.tpl')
%include ('Templates/title.tpl')
%include ('Templates/nav.tpl', loginStateList = loginStateList)

<div id="searchBox">
    <form action ="/search" method="post" align="left">
    <input name="keywords" type = "text" value="{{ctrlList[0]}}" />
    <input value = "Search" type="submit" />
    </form>
</div>

<div id="results">
<table id="resultsTable" >
    %for x in range(len(urlList)):
    <tr>
        <td>
        <a href="{{urlList[x][0]}}">{{urlList[x][0]}}</a>
    </tr>
    %end
</table>

</div>
        %if len(urlList)==0:
           <p> No Results Found.</p>
        </td>
        %end
<div id="pages" align="left">

    Pages:
    %for x in range(1,int(ctrlList[1]+1)):
        %if x == int(ctrlList[2]):
            <b><a href="/search/{{ctrlList[0]}}/{{x}}">{{x}}</a></b>
        %else:
            <a href="/search/{{ctrlList[0]}}/{{x}}">{{x}}</a>
    %end

</div>

%include ('Templates/footer.tpl')
