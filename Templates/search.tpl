%include ('Templates/header.tpl')
%include ('Templates/css.tpl')
%include ('Templates/title.tpl')
%include ('Templates/nav.tpl',loginStateList = loginStateList)

<div id="searchBox">
    <form action ="/search" method="post" align="center" width=300px>
    <input name="keywords" type = "text" />
    <input value = "Search" type="submit" />
    </form>
</div>

%include ('Templates/footer.tpl')



