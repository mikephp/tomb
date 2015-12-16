FROM tomb/ubuntu:base1204

VOLUME ["/home/dirlt/repo"]
VOLUME ["/home/dirlt/KuaiPan"]
EXPOSE 80
EXPOSE 22

RUN apt-get install -y zsh
RUN chsh -s /bin/zsh dirlt

USER dirlt
RUN touch .vmflag
RUN ln -s KuaiPan/private .private
USER root

CMD /usr/sbin/sshd -D
