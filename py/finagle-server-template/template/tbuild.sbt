// coding:utf-8
// Copyright (C) dirlt

import sbtprotobuf.{ProtobufPlugin=>PB}
import AssemblyKeys._

seq(PB.protobufSettings: _*)

assemblySettings

// ====================

name := "%(artifactId)s"

organization := "%(groupId)s"

version := "1.0-SNAPSHOT"

scalaVersion := "2.10.2"

val protobufVersion = "2.4.1"

// fix the issue : package daemon contains object and package with same name: supervisor
// TODO: why is work. -> http://comments.gmane.org/gmane.comp.java.clojure.storm/2426

scalacOptions += "-Yresolve-term-conflict:package"

scalacOptions in Test ++= Seq("-Yrangepos")

libraryDependencies ++= {
  val finagleVersion = "6.6.2"
  val utilVersion = "6.6.0"
  Seq(
    "com.twitter" %%%% "finagle-core" %% finagleVersion,
    "com.twitter" %%%% "finagle-ostrich4" %% finagleVersion,
    "com.twitter" %%%% "finagle-mysql" %% finagleVersion,
    "com.twitter" %%%% "finagle-http" %% finagleVersion,
    "com.twitter" %%%% "util-core" %% utilVersion,
    "com.google.protobuf" %% "protobuf-java" %% protobufVersion,
    "com.google.guava" %% "guava" %% "13.0.1",
    "com.google.code.findbugs" %% "jsr305" %% "1.3.9",
    "org.slf4j" %% "slf4j-log4j12" %% "1.7.5",
    "org.specs2" %%%% "specs2" %% "2.3.4" %% "test"
  )
}

// ====================

// Test Suite

testFrameworks += new TestFramework("org.specs2.runner.SpecsFramework")

parallelExecution in Test := false

publishArtifact in Test := false

// Protocol-Buffers

sourceDirectory in PB.protobufConfig := new java.io.File("src/main/proto")

version in PB.protobufConfig := protobufVersion

// idea takes generated/com as source root, and I can't do nothing about it but manually change it in IDE:(
javaSource in PB.protobufConfig <<= (sourceDirectory in Compile)(_ / "gen-java")

// assembly

mergeStrategy in assembly <<= (mergeStrategy in assembly) { 
  (old) => {
    case "log4j.properties" => MergeStrategy.first 
    case PathList("org","apache","log4j",xs @ _*) => MergeStrategy.first
    case x => old(x)
  }
}

