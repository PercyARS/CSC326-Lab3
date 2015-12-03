<div id="nav">

%item1=loginStateList[0]
%if item1==True:
    <FORM METHOD="LINK" ACTION="/logout" ALIGN = "left" id="logout">
    </FORM>
    %item2 = loginStateList[1]
    {{item2}}

    <button type="submit" form="logout" value="Logout">Logout</button>

%else:
    <FORM METHOD="LINK" ACTION="/login" ALIGN = "left" id="login">
    </FORM>
    <button type="submit" form="login" value="Logout">Login</button>
</div>